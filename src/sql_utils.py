"""Limpieza y validación del SQL generado por el modelo.

El modelo a veces envuelve la consulta en ```sql ... ```, agrega texto antes o
después, o produce varias sentencias. Estas funciones dejan una única consulta
SELECT/WITH limpia y verifican que sea de solo lectura (el proyecto penaliza
con -10 cualquier consulta que modifique la base).
"""
import re

# Palabras clave que indican escritura/DDL: prohibidas.
_PROHIBIDAS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|GRANT|"
    r"REVOKE|MERGE|CALL|LOCK|UNLOCK|SET|USE)\b",
    re.IGNORECASE,
)


def extraer_sql(texto: str) -> str:
    """Extrae la primera consulta SELECT/WITH del texto generado."""
    if not texto:
        return ""

    # 1) Si hay un bloque de código markdown, quedarse con su contenido.
    bloque = re.search(r"```(?:sql)?\s*(.+?)```", texto, re.DOTALL | re.IGNORECASE)
    if bloque:
        texto = bloque.group(1)

    texto = texto.strip()

    # 2) Recortar desde el primer SELECT o WITH que aparezca.
    m = re.search(r"\b(SELECT|WITH)\b", texto, re.IGNORECASE)
    if m:
        texto = texto[m.start():]

    # 3) Quedarse con la primera sentencia (hasta el primer ';').
    #    Si no hay ';', se toma todo el texto restante.
    punto = texto.find(";")
    if punto != -1:
        texto = texto[: punto + 1]

    texto = texto.strip()
    if texto and not texto.endswith(";"):
        texto += ";"
    return texto


def es_solo_lectura(sql: str) -> bool:
    """True si la consulta es SELECT/WITH y no contiene sentencias de escritura."""
    if not sql:
        return False
    sin_comentarios = _quitar_comentarios(sql)
    cabeza = sin_comentarios.lstrip().upper()
    if not (cabeza.startswith("SELECT") or cabeza.startswith("WITH")):
        return False
    return _PROHIBIDAS.search(sin_comentarios) is None


def _quitar_comentarios(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", " ", sql)        # comentarios de línea
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)  # comentarios de bloque
    return sql


def normalizar(sql: str) -> str:
    """Normaliza espacios para comparaciones/logging."""
    return re.sub(r"\s+", " ", sql).strip()
