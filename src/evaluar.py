"""Harness de evaluación: exactitud por ejecución (EX) sobre MySQL 8.4.10.

Reproduce el criterio del evaluador oculto:
  - Se compara el RESULTADO de la consulta, no el texto.
  - El orden de las filas solo cuenta si la pregunta lo pide (columna
    `orden_importa` del CSV de validación).
  - Los números se redondean a 2 decimales.
  - Una columna adicional no penaliza: la predicción acierta si el conjunto de
    columnas de la referencia está contenido (por valores) en la predicción.
  - Métrica: EX ponderada = suma de pesos de aciertos / suma de pesos totales.

Expone:
  - construir_ejecutar(conn, esquema): la función `ejecutar(sql)` que recibe
    generar_sql (solo lectura, máx. 10 filas, dict con ok/columnas/filas/error).
  - evaluar_validacion(generar_sql, csv_val): corre todo el set y devuelve EX y
    el detalle por pregunta (para el análisis de errores).
"""
import csv
from decimal import Decimal

from src.esquemas import TODOS, ddl_esquema, inserts_esquema


# --------------------------------------------------------------------------
# Comparación de resultados
# --------------------------------------------------------------------------
def _norm_valor(v):
    if v is None:
        return None
    if isinstance(v, (int,)):
        return round(float(v), 2)
    if isinstance(v, (float, Decimal)):
        return round(float(v), 2)
    return str(v).strip()


def _norm_fila(fila):
    return tuple(_norm_valor(v) for v in fila)


def _columnas_por_indice(filas):
    """Devuelve lista de columnas (cada una como tupla de valores)."""
    if not filas:
        return []
    ncol = len(filas[0])
    return [tuple(_norm_valor(f[i]) for f in filas) for i in range(ncol)]


def comparar_resultados(ref_filas, pred_filas, orden_importa):
    """True si pred responde la pregunta igual que ref."""
    ref = [_norm_fila(f) for f in ref_filas]
    pred = [_norm_fila(f) for f in pred_filas]

    # Caso escalar / mismas columnas: comparación directa.
    if orden_importa:
        if _contiene_columnas_ordenado(ref, pred):
            return True
    else:
        if _contiene_columnas_desordenado(ref, pred):
            return True
    return False


def _contiene_columnas_desordenado(ref, pred):
    """Cada columna de ref debe existir (como multiconjunto) en pred."""
    if not ref:
        return len(pred) == 0
    ref_cols = _columnas_por_indice(ref)
    pred_cols = _columnas_por_indice(pred)
    if len(ref) != len(pred):
        return False
    pred_disp = [sorted(c, key=lambda x: (x is None, str(x))) for c in pred_cols]
    for rc in ref_cols:
        rc_s = sorted(rc, key=lambda x: (x is None, str(x)))
        if rc_s not in pred_disp:
            return False
    return True


def _contiene_columnas_ordenado(ref, pred):
    """Igual pero respetando el orden de las filas."""
    if not ref:
        return len(pred) == 0
    if len(ref) != len(pred):
        return False
    ref_cols = _columnas_por_indice(ref)
    pred_cols = _columnas_por_indice(pred)
    for rc in ref_cols:
        if list(rc) not in [list(pc) for pc in pred_cols]:
            return False
    return True


# --------------------------------------------------------------------------
# Ejecutor que se entrega a generar_sql
# --------------------------------------------------------------------------
def construir_ejecutar(cur, db):
    """Crea la función ejecutar(sql) para un esquema ya cargado en `db`."""
    def ejecutar(sql):
        try:
            cur.execute(f"USE `{db}`;")
            cur.execute(sql)
            filas = cur.fetchmany(10)
            cols = [d[0] for d in cur.description] if cur.description else []
            return {"ok": True, "columnas": cols,
                    "filas": [list(f) for f in filas], "error": None}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "columnas": [], "filas": [], "error": str(exc)}
    return ejecutar


def _preparar(cur, nombre):
    e = TODOS[nombre]
    db = f"eval_{nombre}"
    cur.execute(f"DROP DATABASE IF EXISTS `{db}`;")
    cur.execute(f"CREATE DATABASE `{db}` CHARACTER SET utf8mb4;")
    cur.execute(f"USE `{db}`;")
    for s in ddl_esquema(e).split(";"):
        if s.strip():
            cur.execute(s)
    for s in inserts_esquema(e).split(";"):
        if s.strip():
            cur.execute(s)
    return db


# --------------------------------------------------------------------------
# Evaluación completa
# --------------------------------------------------------------------------
def evaluar_validacion(generar_sql, csv_val="datos/validacion/validacion_propia.csv",
                       host="127.0.0.1", port=3306, user="root", password="root",
                       usar_ejecutar=False):
    """Evalúa generar_sql sobre el set de validación. Devuelve (ex, detalle)."""
    import pymysql
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                           charset="utf8mb4", autocommit=True)
    cur = conn.cursor()

    with open(csv_val, encoding="utf-8") as f:
        preguntas = list(csv.DictReader(f))

    bases = {}
    for nombre in sorted({p["esquema"] for p in preguntas}):
        bases[nombre] = _preparar(cur, nombre)

    detalle = []
    acierto_peso = 0
    total_peso = 0
    for p in preguntas:
        esquema_nombre = p["esquema"]
        db = bases[esquema_nombre]
        peso = int(p["peso"])
        orden = int(p.get("orden_importa", 0))
        ddl = ddl_esquema(TODOS[esquema_nombre])

        ejecutar = construir_ejecutar(cur, db) if usar_ejecutar else None
        try:
            pred_sql = generar_sql(ddl, p["pregunta"], ejecutar)
        except Exception as exc:  # noqa: BLE001
            detalle.append({**p, "pred_sql": f"ERROR: {exc}", "acierto": 0,
                            "categoria_error": "excepcion"})
            total_peso += peso
            continue

        # Ejecutar referencia y predicción.
        cur.execute(f"USE `{db}`;")
        cur.execute(p["sql_referencia"])
        ref_filas = cur.fetchall()

        ok_exec = True
        err = None
        try:
            cur.execute(f"USE `{db}`;")
            cur.execute(pred_sql)
            pred_filas = cur.fetchall()
        except Exception as exc:  # noqa: BLE001
            ok_exec = False
            err = str(exc)
            pred_filas = []

        acierto = 0
        categoria = None
        if ok_exec:
            acierto = 1 if comparar_resultados(ref_filas, pred_filas, orden) else 0
            if not acierto:
                categoria = "resultado_distinto"
        else:
            from src.validar_mysql import categoria_error
            categoria = categoria_error(err)

        acierto_peso += acierto * peso
        total_peso += peso
        detalle.append({
            "id": p.get("id"), "esquema": esquema_nombre, "nivel": p["nivel"],
            "peso": peso, "pregunta": p["pregunta"],
            "sql_referencia": p["sql_referencia"], "pred_sql": pred_sql,
            "acierto": acierto, "categoria_error": categoria,
        })

    cur.close()
    conn.close()
    ex = acierto_peso / total_peso if total_peso else 0.0
    return ex, detalle


def guardar_detalle(detalle, ruta):
    campos = ["id", "esquema", "nivel", "peso", "pregunta", "sql_referencia",
              "pred_sql", "acierto", "categoria_error"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for d in detalle:
            w.writerow({k: d.get(k, "") for k in campos})
