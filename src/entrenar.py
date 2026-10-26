"""Fine-tuning con LoRA del modelo base para Text-to-SQL.

Entrena un adapter LoRA sobre Qwen2.5-Coder-1.5B-Instruct usando los pares de
datos/entrenamiento/train.jsonl y el mismo prompt que usa solucion.py
(src/prompt.py). La loss se calcula SOLO sobre la respuesta (el SQL), no sobre
el prompt, enmascarando las etiquetas del prompt.

Dos configuraciones (difieren en UN SOLO factor: el rank r de LoRA):
  config A -> r = 8   (hipótesis: suficiente capacidad, entrena más rápido)
  config B -> r = 32  (hipótesis: más capacidad -> mejor EX en consultas difíciles)
Todo lo demás (alpha/r = 2, dropout, lr, épocas, módulos) se mantiene igual.

Pensado para Google Colab con GPU T4. Uso:
    from src.entrenar import entrenar
    entrenar(config="A", salida="adapter_A")   # o config="B"
"""
import json
import os

CONFIGS = {
    "A": {"r": 8, "lora_alpha": 16},
    "B": {"r": 32, "lora_alpha": 64},
}

# Módulos objetivo de LoRA en la arquitectura Qwen2.
MODULOS_OBJETIVO = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

MODELO_BASE = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
MAX_LEN = 1024


def _cargar_pares(ruta="datos/entrenamiento/train.jsonl"):
    pares = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                pares.append(json.loads(linea))
    return pares


def _construir_dataset(tokenizer, pares):
    """Tokeniza cada par enmascarando el prompt (labels=-100 en el prompt)."""
    from src.prompt import construir_mensajes

    ejemplos = []
    for p in pares:
        mensajes = construir_mensajes(p["esquema"], p["pregunta"])
        # Texto del prompt (hasta donde empieza la respuesta del asistente).
        prompt_ids = tokenizer.apply_chat_template(
            mensajes, tokenize=True, add_generation_prompt=True,
        )
        respuesta = p["sql"].strip()
        resp_ids = tokenizer(respuesta + tokenizer.eos_token,
                             add_special_tokens=False)["input_ids"]

        input_ids = prompt_ids + resp_ids
        labels = [-100] * len(prompt_ids) + resp_ids[:]  # loss solo en la respuesta

        input_ids = input_ids[:MAX_LEN]
        labels = labels[:MAX_LEN]
        ejemplos.append({
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": [1] * len(input_ids),
        })
    return ejemplos


class _Colador:
    """Data collator con padding dinámico que respeta labels=-100."""
    def __init__(self, tokenizer):
        self.pad = tokenizer.pad_token_id

    def __call__(self, batch):
        import torch
        maxlen = max(len(b["input_ids"]) for b in batch)
        ids, lab, att = [], [], []
        for b in batch:
            n = maxlen - len(b["input_ids"])
            ids.append(b["input_ids"] + [self.pad] * n)
            lab.append(b["labels"] + [-100] * n)
            att.append(b["attention_mask"] + [0] * n)
        return {
            "input_ids": torch.tensor(ids),
            "labels": torch.tensor(lab),
            "attention_mask": torch.tensor(att),
        }


def entrenar(config="A", salida="adapter_A", epocas=3, lr=2e-4,
             batch=8, grad_accum=2, usar_qlora=True, semilla=2026,
             ruta_datos="datos/entrenamiento/train.jsonl", max_pasos=-1):
    """Entrena un adapter LoRA/QLoRA y lo guarda en `salida/`.

    Devuelve un dict con parámetros entrenables, tiempo e historial de loss
    (para reportar las curvas exigidas por el PDF).
    """
    import time
    import torch
    from transformers import (
        AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    torch.manual_seed(semilla)
    cfg = CONFIGS[config]

    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Cuantización 4-bit (QLoRA) para que entre en una T4.
    quant_cfg = None
    if usar_qlora:
        from transformers import BitsAndBytesConfig
        quant_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    modelo = AutoModelForCausalLM.from_pretrained(
        MODELO_BASE,
        quantization_config=quant_cfg,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    if usar_qlora:
        modelo = prepare_model_for_kbit_training(modelo)

    lora = LoraConfig(
        r=cfg["r"],
        lora_alpha=cfg["lora_alpha"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=MODULOS_OBJETIVO,
    )
    modelo = get_peft_model(modelo, lora)

    entrenables = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    totales = sum(p.numel() for p in modelo.parameters())

    pares = _cargar_pares(ruta_datos)
    datos = _construir_dataset(tokenizer, pares)

    args = TrainingArguments(
        output_dir=f"runs/{salida}",
        num_train_epochs=epocas,
        max_steps=max_pasos,
        per_device_train_batch_size=batch,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=20,
        save_strategy="no",
        fp16=True,
        optim="paged_adamw_8bit" if usar_qlora else "adamw_torch",
        report_to="none",
        seed=semilla,
    )

    trainer = Trainer(
        model=modelo,
        args=args,
        train_dataset=datos,
        data_collator=_Colador(tokenizer),
    )

    t0 = time.time()
    trainer.train()
    dt = time.time() - t0

    os.makedirs(salida, exist_ok=True)
    modelo.save_pretrained(salida)
    tokenizer.save_pretrained(salida)

    hist = [h for h in trainer.state.log_history if "loss" in h]
    reporte = {
        "config": config,
        "r": cfg["r"],
        "lora_alpha": cfg["lora_alpha"],
        "parametros_entrenables": entrenables,
        "parametros_totales": totales,
        "porcentaje_entrenable": round(100 * entrenables / totales, 4),
        "tiempo_segundos": round(dt, 1),
        "epocas": epocas,
        "max_pasos": max_pasos,
        "n_pares": len(pares),
        "loss_history": hist,
    }
    with open(os.path.join(salida, "reporte_entrenamiento.json"), "w",
              encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print(f"[{config}] entrenables={entrenables:,} "
          f"({reporte['porcentaje_entrenable']}%)  tiempo={dt:.0f}s")
    return reporte


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=["A", "B"], default="A")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--epocas", type=int, default=3)
    args = ap.parse_args()
    salida = args.salida or f"adapter_{args.config}"
    entrenar(config=args.config, salida=salida, epocas=args.epocas)
