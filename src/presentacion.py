"""Genera presentacion.pdf (máx. 12 diapositivas) y resultados/curvas_loss.png.

Lee los reportes de entrenamiento (adapter_A/, adapter_B/ o adapter/) si existen.
Uso: python -m src.presentacion
"""
import json
import os

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

W, H = landscape(A4)


def _reporte(nombre):
    for ruta in (f"{nombre}/reporte_entrenamiento.json",
                 f"resultados/reporte_{nombre}.json"):
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                return json.load(f)
    return None


def _curvas(reportes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    hay = False
    plt.figure(figsize=(7, 4))
    for nombre, r in reportes.items():
        if r and r.get("loss_history"):
            hay = True
            pasos = [h["step"] for h in r["loss_history"]]
            loss = [h["loss"] for h in r["loss_history"]]
            plt.plot(pasos, loss, marker="o", label=f"{nombre} (r={r['r']})")
    if not hay:
        plt.close()
        return None
    plt.xlabel("paso"); plt.ylabel("loss"); plt.legend(); plt.title("Curvas de loss")
    os.makedirs("resultados", exist_ok=True)
    ruta = "resultados/curvas_loss.png"
    plt.savefig(ruta, dpi=120, bbox_inches="tight"); plt.close()
    return ruta


def _diapositiva(c, titulo, lineas, imagen=None):
    c.setFont("Helvetica-Bold", 26)
    c.drawString(50, H - 70, titulo)
    c.setLineWidth(2); c.line(50, H - 82, W - 50, H - 82)
    y = H - 125
    for linea in lineas:
        tam = 15 if not linea.startswith("  ") else 13
        c.setFont("Helvetica", tam)
        c.drawString(60, y, linea)
        y -= 26
    if imagen and os.path.exists(imagen):
        c.drawImage(imagen, W / 2 - 40, 50, width=W / 2, height=H / 2 + 40,
                    preserveAspectRatio=True)
    c.showPage()


def _fmt_reporte(nombre, r):
    if not r:
        return [f"{nombre}: pendiente de entrenar"]
    return [
        f"{nombre}: r={r['r']}, alpha={r['lora_alpha']}",
        f"  parámetros entrenables: {r['parametros_entrenables']:,} "
        f"({r['porcentaje_entrenable']}% del total)",
        f"  tiempo de entrenamiento: {r['tiempo_segundos']/60:.1f} min (T4, LoRA fp16)",
        f"  pasos: {r.get('max_pasos', '-')}, pares: {r['n_pares']}, "
        f"loss final: {r['loss_history'][-1]['loss']:.3f}" if r.get("loss_history") else "",
    ]


def main():
    with open("datos/entrenamiento/resumen.json", encoding="utf-8") as f:
        resumen = json.load(f)
    rep_A = _reporte("adapter_A")
    rep_B = _reporte("adapter_B")
    curvas = _curvas({"A": rep_A, "B": rep_B})

    ex = {}
    if os.path.exists("resultados/validacion_propia.csv"):
        import csv
        with open("resultados/validacion_propia.csv", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                if fila.get("EX") not in (None, "", "pendiente"):
                    ex[fila["configuracion"]] = fila["EX"]

    c = canvas.Canvas("presentacion.pdf", pagesize=landscape(A4))
    _diapositiva(c, "Text-to-SQL con LoRA", [
        "Proyecto 3 · Deep Learning 2026 · Universidad del Valle",
        "Pablo · Luis Palacios",
        "",
        "Qwen2.5-Coder-1.5B-Instruct + adapter LoRA (fp16)",
        "Esquema (CREATE TABLE con COMMENT) + pregunta en español -> MySQL 8.4",
    ])
    _diapositiva(c, "Problema y contrato", [
        "generar_sql(esquema, pregunta, ejecutar=None) -> una sola SELECT / WITH",
        "Generación determinista (do_sample=False, semilla 2026)",
        "config.json: usar_adapter true/false con el MISMO prompt",
        "Salida filtrada a solo lectura (nunca modifica la base)",
        "Métrica: EX ponderada (fácil 1, media 2, difícil 3)",
    ])
    niveles = resumen["por_nivel"]
    _diapositiva(c, "Dataset de entrenamiento", [
        f"{resumen['total']:,} pares pregunta–SQL sobre 10 esquemas propios",
        f"  fácil: {niveles['facil']} · media: {niveles['media']} · difícil: {niveles['dificil']}",
        "Nombres en español e inglés, con abreviaturas (hr, fleet, clinic...)",
        "Plantillas por nivel: filtros, JOIN, GROUP BY/HAVING, subconsultas,",
        "  WITH, funciones de ventana y fechas",
        "Pares validados ejecutándose en MySQL 8.4.10 (ONLY_FULL_GROUP_BY)",
    ])
    _diapositiva(c, "Validación propia", [
        "2 esquemas NO vistos en entrenamiento: aerolinea y banco",
        "40 preguntas escritas por el equipo, en los tres niveles",
        "Partición por esquema, no por pregunta (evita fuga de esquema)",
        "Harness (src/evaluar.py) replica las reglas del evaluador:",
        "  orden solo si se pide, redondeo a 2 decimales, columna extra no penaliza",
    ])
    _diapositiva(c, "Configuraciones LoRA (un solo factor: rank r)", [
        "Mismo lr (2e-4), dropout 0.05, alpha/r = 2, 100 pasos, batch 2x8 acum., q,k,v,o,gate,up,down",
        "Loss solo sobre la respuesta SQL (prompt enmascarado)",
        "Hipótesis A (r=8): rank bajo basta para el patrón SQL y entrena más rápido",
        "Hipótesis B (r=32): más capacidad ayuda en consultas difíciles",
        "  (subconsultas, ventanas), a costa de más parámetros y tiempo",
    ])
    _diapositiva(c, "Resultados de entrenamiento",
                 _fmt_reporte("Config A", rep_A) + [""] + _fmt_reporte("Config B", rep_B))
    if curvas:
        _diapositiva(c, "Curvas de loss", ["Loss de entrenamiento por paso"], curvas)
    filas_ex = [f"{k}: EX = {v}" for k, v in ex.items()] or [
        "EX en validación propia: ver resultados/validacion_propia.csv",
        "(notebook 03_evaluacion.ipynb con MySQL 8.4.10)",
    ]
    _diapositiva(c, "Baseline vs adapter (validación propia)", filas_ex)
    _diapositiva(c, "Experimento de inferencia: auto-corrección", [
        "Si el evaluador entrega ejecutar(sql), se ejecuta la consulta generada",
        "Si MySQL devuelve error, se re-genera con el mensaje de error como pista",
        "Máximo 3 llamadas a ejecutar por pregunta; siempre se devuelve SELECT",
        "Ataca errores de sintaxis y columnas/tablas inexistentes,",
        "  no corrige errores lógicos (resultado distinto)",
    ])
    _diapositiva(c, "Análisis de errores por categoría", [
        "Categorías: sintaxis, columna/tabla inexistente, JOIN, agregación,",
        "  filtro, resultado distinto",
        "Esperado: el baseline falla más por formato y nombres inventados;",
        "  el adapter aprende el formato y a usar los COMMENT del esquema",
        "Lo difícil (ventanas, fechas, WITH) concentra los errores restantes",
    ])
    _diapositiva(c, "Predicción justificada de EX (evaluación oculta)", [
        "Predicción con adapter: EX ~ 0.45–0.55; sin adapter: ~ 0.30–0.40",
        "Justificación:",
        "  - el modelo base 1.5B ya resuelve bien preguntas de una tabla (peso 1)",
        "  - el adapter mejora formato, uso de COMMENT y JOIN/GROUP BY (peso 2)",
        "  - las difíciles (peso 3) siguen siendo el cuello de botella",
        "  - esquemas ocultos con nombres abreviados -> algo de caída vs validación",
        "  - entrenamiento corto (100 pasos, ~0.8 épocas) limita la mejora",
    ])
    _diapositiva(c, "Conclusiones y trabajo futuro", [
        "Pipeline completo: datos validados, LoRA A/B, harness EX, auto-corrección",
        "Siguiente paso: más épocas, más datos difíciles (Spider/BIRD traducidos),",
        "  few-shot con ejemplos del mismo esquema",
        "Base para el Proyecto Final: adapter, prompt, dataset y evaluador",
    ])
    c.save()
    print("presentacion.pdf generado")


if __name__ == "__main__":
    main()
