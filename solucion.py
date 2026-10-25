"""Contrato de entrega — Proyecto 3 Text-to-SQL.

Carga el modelo indicado en config.json y expone:

    generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str

- Carga del modelo: una sola vez, en memoria (< 5 min).
- Generación determinista (do_sample=False, semilla fija de config.json).
- Devuelve una única consulta SELECT o WITH ... SELECT, de solo lectura.
- Si el evaluador entrega `ejecutar`, se usa para auto-corregir la consulta
  (máximo 3 llamadas por pregunta) — este es el experimento de inferencia.
- Con "usar_adapter": false usa el modelo base con el MISMO prompt (baseline).
"""
import json
import os
import sys

import torch

# Permite importar el paquete src/ sin importar desde dónde se ejecute.
_RAIZ = os.path.dirname(os.path.abspath(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from src.prompt import construir_prompt            # noqa: E402
from src.sql_utils import extraer_sql, es_solo_lectura, normalizar  # noqa: E402

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
_CONFIG_PATH = os.path.join(_RAIZ, "config.json")
with open(_CONFIG_PATH, encoding="utf-8") as f:
    CONFIG = json.load(f)

MODELO_BASE = CONFIG["modelo_base"]
ADAPTER = CONFIG.get("adapter", "adapter/")
USAR_ADAPTER = bool(CONFIG.get("usar_adapter", True))
SEMILLA = int(CONFIG.get("semilla", 2026))

MAX_NEW_TOKENS = int(CONFIG.get("max_new_tokens", 384))
MAX_INTENTOS_CORRECCION = 2  # + intento inicial = hasta 3 llamadas a ejecutar

# Estado global (se inicializa una sola vez).
_tokenizer = None
_modelo = None


# --------------------------------------------------------------------------
# Carga del modelo
# --------------------------------------------------------------------------
def _fijar_semilla():
    import random
    import numpy as np
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    torch.manual_seed(SEMILLA)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEMILLA)


def cargar_modelo():
    """Carga tokenizer + modelo (+ adapter si corresponde). Idempotente."""
    global _tokenizer, _modelo
    if _modelo is not None:
        return

    from transformers import AutoModelForCausalLM, AutoTokenizer

    _fijar_semilla()

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    device_map = "auto" if torch.cuda.is_available() else None

    _tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE, trust_remote_code=True)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token

    modelo = AutoModelForCausalLM.from_pretrained(
        MODELO_BASE,
        torch_dtype=dtype,
        device_map=device_map,
        trust_remote_code=True,
    )

    if USAR_ADAPTER:
        ruta_adapter = ADAPTER if os.path.isabs(ADAPTER) else os.path.join(_RAIZ, ADAPTER)
        if os.path.isdir(ruta_adapter) and os.path.exists(
            os.path.join(ruta_adapter, "adapter_config.json")
        ):
            from peft import PeftModel
            modelo = PeftModel.from_pretrained(modelo, ruta_adapter)
            modelo = modelo.merge_and_unload()  # fusiona para inferencia más rápida
        else:
            print(
                f"[solucion] AVISO: usar_adapter=true pero no se encontró un "
                f"adapter válido en {ruta_adapter}; se usa el modelo base.",
                file=sys.stderr,
            )

    if device_map is None and torch.cuda.is_available():
        modelo = modelo.to("cuda")

    modelo.eval()
    _modelo = modelo


# --------------------------------------------------------------------------
# Generación
# --------------------------------------------------------------------------
def _generar_crudo(esquema: str, pregunta: str, feedback: str = "") -> str:
    """Una pasada de generación determinista; devuelve el texto decodificado."""
    prompt = construir_prompt(_tokenizer, esquema, pregunta)
    if feedback:
        prompt += feedback  # se inyecta tras el prompt de generación

    # add_special_tokens=False: el chat_template ya incluye los tokens de
    # control, así que se tokeniza igual que en entrenamiento (sin duplicar).
    entradas = _tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    entradas = {k: v.to(_modelo.device) for k, v in entradas.items()}

    with torch.no_grad():
        salida = _modelo.generate(
            **entradas,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,          # determinista
            num_beams=1,
            temperature=None,
            top_p=None,
            top_k=None,
            pad_token_id=_tokenizer.pad_token_id,
        )
    nuevos = salida[0][entradas["input_ids"].shape[1]:]
    return _tokenizer.decode(nuevos, skip_special_tokens=True)


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    """Genera una consulta MySQL para la pregunta dada sobre el esquema.

    Si `ejecutar` está disponible, intenta ejecutar la consulta y, ante un
    error, pide al modelo una corrección (hasta 3 llamadas a `ejecutar` en
    total). Siempre devuelve una sola consulta SELECT/WITH de solo lectura.
    """
    cargar_modelo()

    texto = _generar_crudo(esquema, pregunta)
    sql = extraer_sql(texto)
    if not es_solo_lectura(sql):
        # Reintento limpio: a veces el modelo divaga; forzamos una pasada más.
        sql_retry = extraer_sql(_generar_crudo(esquema, pregunta))
        if es_solo_lectura(sql_retry):
            sql = sql_retry

    # Experimento de inferencia: auto-corrección con el ejecutor del evaluador.
    if ejecutar is not None and es_solo_lectura(sql):
        llamadas = 0
        while llamadas < MAX_INTENTOS_CORRECCION + 1:
            try:
                res = ejecutar(sql)
            except Exception:
                break
            llamadas += 1
            if isinstance(res, dict) and res.get("ok"):
                break  # la consulta corre: la aceptamos
            error = (res or {}).get("error", "") if isinstance(res, dict) else ""
            if not error or llamadas > MAX_INTENTOS_CORRECCION:
                break
            feedback = (
                "\nLa consulta anterior dio este error de MySQL:\n"
                f"{error}\n"
                "Corrige la consulta. Devuelve solo la consulta MySQL corregida:\n"
                f"Consulta con error:\n{normalizar(sql)}\n"
                "### Consulta MySQL corregida:"
            )
            nuevo = extraer_sql(_generar_crudo(esquema, pregunta, feedback))
            if es_solo_lectura(nuevo) and normalizar(nuevo) != normalizar(sql):
                sql = nuevo
            else:
                break

    if not es_solo_lectura(sql):
        # Último recurso: nunca devolver algo que no sea SELECT.
        return "SELECT 1;"
    return sql


if __name__ == "__main__":
    # Prueba rápida de humo (requiere el modelo descargado).
    esquema_demo = (
        "CREATE TABLE empleados (\n"
        "  id INT PRIMARY KEY,\n"
        "  nombre VARCHAR(100),\n"
        "  salario DECIMAL(10,2),\n"
        "  departamento VARCHAR(50)\n"
        ");"
    )
    print(generar_sql(esquema_demo, "¿Cuántos empleados hay por departamento?"))
