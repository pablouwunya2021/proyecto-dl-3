"""Exporta el dataset a archivos del repositorio.

Produce:
  datos/entrenamiento/train.jsonl        pares de entrenamiento (deduplicados)
  datos/entrenamiento/resumen.json       conteos por nivel y por esquema
  datos/validacion/validacion_propia.csv  40 preguntas propias (2 esquemas nuevos)
  datos/validacion/validacion_propia.jsonl

El train.jsonl es el conjunto SINTÉTICO antes de la validación en MySQL. El
notebook notebooks/01_datos.ipynb lo pasa por src.validar_mysql.validar_pares y
reescribe el archivo solo con los pares que ejecutan sin error, registrando los
descartes en datos/descartes/.
"""
import csv
import json
import os
from collections import Counter

from src.generar_datos import (
    generar_entrenamiento, generar_validacion_sintetica,
)


def _dedup(pares):
    vistos = set()
    out = []
    for p in pares:
        clave = (p["esquema"], p["pregunta"].strip().lower(), p["sql"].strip())
        if clave in vistos:
            continue
        vistos.add(clave)
        out.append(p)
    return out


def exportar_entrenamiento():
    pares = _dedup(generar_entrenamiento())
    os.makedirs("datos/entrenamiento", exist_ok=True)
    ruta = "datos/entrenamiento/train.jsonl"
    with open(ruta, "w", encoding="utf-8") as f:
        for p in pares:
            f.write(json.dumps({
                "esquema": p["ddl"],
                "esquema_nombre": p["esquema"],
                "pregunta": p["pregunta"],
                "sql": p["sql"],
                "nivel": p["nivel"],
                "peso": p["peso"],
            }, ensure_ascii=False) + "\n")

    resumen = {
        "total": len(pares),
        "por_nivel": dict(Counter(p["nivel"] for p in pares)),
        "por_esquema": dict(Counter(p["esquema"] for p in pares)),
    }
    with open("datos/entrenamiento/resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(f"train.jsonl: {len(pares)} pares  ->  {resumen['por_nivel']}")
    return pares


def exportar_validacion_propia(n_por_nivel=(16, 12, 12)):
    """Selecciona 40 preguntas balanceadas sobre los 2 esquemas de validación.

    Es el punto de partida del validation set propio: revísenlo y ajústenlo a
    mano para que sean 'sus' preguntas, pero ya quedan ejecutables y balanceadas.
    """
    pares = generar_validacion_sintetica()
    por_nivel = {"facil": [], "media": [], "dificil": []}
    for p in pares:
        por_nivel[p["nivel"]].append(p)

    sel = []
    objetivo = dict(zip(["facil", "media", "dificil"], n_por_nivel))
    for nivel, n in objetivo.items():
        cand = por_nivel[nivel]
        # Repartir entre los esquemas de validación de forma alternada.
        cand_ordenado = sorted(cand, key=lambda x: (x["esquema"], x["pregunta"]))
        paso = max(1, len(cand_ordenado) // n)
        sel.extend(cand_ordenado[::paso][:n])

    os.makedirs("datos/validacion", exist_ok=True)
    with open("datos/validacion/validacion_propia.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "esquema", "nivel", "peso", "pregunta",
                    "sql_referencia", "orden_importa"])
        for i, p in enumerate(sel, 1):
            orden = 1 if ("ORDER BY" in p["sql"] and "LIMIT" not in p["sql"]) else 0
            w.writerow([i, p["esquema"], p["nivel"], p["peso"],
                        p["pregunta"], p["sql"], orden])

    with open("datos/validacion/validacion_propia.jsonl", "w",
              encoding="utf-8") as f:
        for i, p in enumerate(sel, 1):
            f.write(json.dumps({
                "id": i, "esquema_nombre": p["esquema"], "nivel": p["nivel"],
                "peso": p["peso"], "pregunta": p["pregunta"],
                "sql_referencia": p["sql"], "ddl": p["ddl"],
            }, ensure_ascii=False) + "\n")

    print(f"validacion_propia: {len(sel)} preguntas  ->  "
          f"{dict(Counter(p['nivel'] for p in sel))}")
    return sel


if __name__ == "__main__":
    exportar_entrenamiento()
    exportar_validacion_propia()
