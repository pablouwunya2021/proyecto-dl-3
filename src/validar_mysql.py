"""Validación de pares pregunta–SQL contra MySQL 8.4.10.

El PDF exige que solo se conserven los pares cuya consulta se ejecute sin error
en MySQL 8.4.10 (config por defecto, con ONLY_FULL_GROUP_BY). Este módulo:

1. Crea cada esquema y carga sus datos de ejemplo en una base temporal.
2. Ejecuta cada SQL candidato; si da error, lo descarta y registra el motivo.
3. Devuelve (conservados, descartados) para auditar cuántos se descartaron.

Uso típico (requiere un MySQL 8.4.10 accesible):
    docker run -d --name mysql84 -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.4.10
    pip install pymysql
    python -m src.validar_mysql

Si no hay MySQL disponible, importar validar_pares() desde el notebook de datos
en Colab (allí sí se instala el servidor).
"""
import os

from src.esquemas import TODOS, ddl_esquema, inserts_esquema


def _conectar(host, port, user, password):
    import pymysql
    return pymysql.connect(
        host=host, port=port, user=user, password=password,
        charset="utf8mb4", autocommit=True,
    )


def _preparar_bases(cur, nombres_esquema):
    """Crea una base por esquema con su DDL y sus datos de ejemplo."""
    for nombre in nombres_esquema:
        e = TODOS[nombre]
        db = f"val_{nombre}"
        cur.execute(f"DROP DATABASE IF EXISTS `{db}`;")
        cur.execute(f"CREATE DATABASE `{db}` CHARACTER SET utf8mb4;")
        cur.execute(f"USE `{db}`;")
        for sent in ddl_esquema(e).split(";"):
            if sent.strip():
                cur.execute(sent)
        ins = inserts_esquema(e)
        for sent in ins.split(";"):
            if sent.strip():
                cur.execute(sent)


def validar_pares(pares, host="127.0.0.1", port=3306, user="root", password="root"):
    """Ejecuta cada par en MySQL. Devuelve (conservados, descartados).

    `descartados` incluye el motivo de error para el reporte de descartes.
    """
    conn = _conectar(host, port, user, password)
    cur = conn.cursor()

    esquemas = sorted({p["esquema"] for p in pares})
    _preparar_bases(cur, esquemas)

    conservados, descartados = [], []
    for p in pares:
        try:
            cur.execute(f"USE `val_{p['esquema']}`;")
            cur.execute(p["sql"])
            cur.fetchall()
            conservados.append(p)
        except Exception as exc:  # noqa: BLE001
            d = dict(p)
            d["motivo_descarte"] = str(exc)[:300]
            descartados.append(d)

    cur.close()
    conn.close()
    return conservados, descartados


def categoria_error(mensaje: str) -> str:
    """Clasifica un error de MySQL para el análisis de descartes/errores."""
    m = (mensaje or "").lower()
    if "syntax" in m:
        return "sintaxis"
    if "unknown column" in m:
        return "columna_inexistente"
    if "doesn't exist" in m or "unknown table" in m:
        return "tabla_inexistente"
    if "only_full_group_by" in m or "group by" in m:
        return "group_by"
    if "ambiguous" in m:
        return "columna_ambigua"
    return "otro"


if __name__ == "__main__":
    from src.generar_datos import generar_entrenamiento
    import csv

    pares = generar_entrenamiento()
    print(f"Generados: {len(pares)} pares. Validando en MySQL...")
    try:
        ok, descarte = validar_pares(pares)
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo conectar a MySQL ({exc}).")
        print("Levanta MySQL 8.4.10 (ver docstring) y reintenta.")
        raise SystemExit(1)

    print(f"Conservados: {len(ok)}  |  Descartados: {len(descarte)}")
    from collections import Counter
    cats = Counter(categoria_error(d["motivo_descarte"]) for d in descarte)
    print("Descartes por categoría:", dict(cats))

    os.makedirs("datos/descartes", exist_ok=True)
    with open("datos/descartes/descartes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["esquema", "nivel", "pregunta", "sql", "categoria", "motivo"])
        for d in descarte:
            w.writerow([d["esquema"], d["nivel"], d["pregunta"], d["sql"],
                        categoria_error(d["motivo_descarte"]), d["motivo_descarte"]])
    print("Descartes guardados en datos/descartes/descartes.csv")
