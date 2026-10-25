"""Generador de pares pregunta–SQL sintéticos sobre los esquemas propios.

Estrategia: plantillas por nivel de dificultad (fácil / media / difícil) que
recorren las tablas y columnas de cada esquema. Como el SQL se construye a
partir de la estructura real del esquema, es sintácticamente válido y referencia
solo columnas existentes; aun así, todos los pares se validan ejecutándolos en
MySQL 8.4.10 (ver notebooks/01_datos.ipynb y src/validar_mysql.py) antes de
usarse — solo se conservan los que corren sin error.

Cada par: {esquema, nivel, peso, pregunta, sql, columnas}.
  nivel fácil  -> peso 1 (una tabla)
  nivel media  -> peso 2 (JOIN, GROUP BY, HAVING)
  nivel difícil-> peso 3 (subconsultas, WITH, ventanas, fechas)
"""
import itertools
import random

from src.esquemas import (
    Esquema, Tabla, Columna, ddl_esquema,
    ESQUEMAS_ENTRENAMIENTO, ESQUEMAS_VALIDACION,
)

PESO = {"facil": 1, "media": 2, "dificil": 3}


def _cols(t: Tabla, rol):
    return [c for c in t.columnas if c.rol == rol]


def _par(e, nivel, pregunta, sql, columnas):
    return {
        "esquema": e.nombre,
        "nivel": nivel,
        "peso": PESO[nivel],
        "pregunta": pregunta,
        "sql": sql,
        "columnas": columnas,
    }


# --------------------------------------------------------------------------
# Nivel FÁCIL — una sola tabla
# --------------------------------------------------------------------------
def _faciles(e: Esquema):
    pares = []
    for t in e.tablas:
        num = _cols(t, "numero")
        cat = _cols(t, "categoria")
        txt = _cols(t, "texto")
        fecha = _cols(t, "fecha")

        # Conteo total de filas
        pares.append(_par(e, "facil",
            f"¿Cuántos registros hay en la tabla {t.nombre}?",
            f"SELECT COUNT(*) FROM {t.nombre};", ["COUNT(*)"]))

        # Agregaciones sobre columnas numéricas
        for c in num:
            pares.append(_par(e, "facil",
                f"¿Cuál es el valor máximo de {c.comentario or c.nombre} en {t.nombre}?",
                f"SELECT MAX({c.nombre}) FROM {t.nombre};", [f"MAX({c.nombre})"]))
            pares.append(_par(e, "facil",
                f"¿Cuál es el valor mínimo de {c.comentario or c.nombre} en {t.nombre}?",
                f"SELECT MIN({c.nombre}) FROM {t.nombre};", [f"MIN({c.nombre})"]))
            pares.append(_par(e, "facil",
                f"¿Cuál es el promedio de {c.comentario or c.nombre} en {t.nombre}?",
                f"SELECT AVG({c.nombre}) FROM {t.nombre};", [f"AVG({c.nombre})"]))
            pares.append(_par(e, "facil",
                f"¿Cuál es la suma total de {c.comentario or c.nombre} en {t.nombre}?",
                f"SELECT SUM({c.nombre}) FROM {t.nombre};", [f"SUM({c.nombre})"]))

        # Listar valores distintos de una categórica y contarlos
        for c in cat:
            pares.append(_par(e, "facil",
                f"Lista los valores distintos de {c.comentario or c.nombre} en {t.nombre}.",
                f"SELECT DISTINCT {c.nombre} FROM {t.nombre};", [c.nombre]))
            pares.append(_par(e, "facil",
                f"¿Cuántos valores distintos de {c.comentario or c.nombre} hay en {t.nombre}?",
                f"SELECT COUNT(DISTINCT {c.nombre}) FROM {t.nombre};",
                [f"COUNT(DISTINCT {c.nombre})"]))
            # Filtro por cada valor del dominio
            for v in (c.valores or []):
                col_ret = (txt[0].nombre if txt else
                           [col.nombre for col in t.columnas if col.pk][0])
                pares.append(_par(e, "facil",
                    f"Muestra el {col_ret} de los registros de {t.nombre} "
                    f"con {c.comentario or c.nombre} igual a '{v}'.",
                    f"SELECT {col_ret} FROM {t.nombre} WHERE {c.nombre} = '{v}';",
                    [col_ret]))
                pares.append(_par(e, "facil",
                    f"¿Cuántos registros de {t.nombre} tienen "
                    f"{c.comentario or c.nombre} igual a '{v}'?",
                    f"SELECT COUNT(*) FROM {t.nombre} WHERE {c.nombre} = '{v}';",
                    ["COUNT(*)"]))

        # Top-N y filtro por umbral sobre numérica, ordenando por texto
        if num and txt:
            cn = num[0].nombre
            ct = txt[0].nombre
            pares.append(_par(e, "facil",
                f"Muestra los 3 registros de {t.nombre} con mayor {num[0].comentario or cn}. "
                f"Devuelve {ct} y {cn}.",
                f"SELECT {ct}, {cn} FROM {t.nombre} ORDER BY {cn} DESC LIMIT 3;",
                [ct, cn]))
            pares.append(_par(e, "facil",
                f"Ordena los registros de {t.nombre} por {num[0].comentario or cn} "
                f"de menor a mayor. Devuelve {ct} y {cn}.",
                f"SELECT {ct}, {cn} FROM {t.nombre} ORDER BY {cn} ASC;", [ct, cn]))
            pares.append(_par(e, "facil",
                f"¿Cuál es el registro de {t.nombre} con mayor "
                f"{num[0].comentario or cn}? Devuelve {ct} y {cn}.",
                f"SELECT {ct}, {cn} FROM {t.nombre} ORDER BY {cn} DESC LIMIT 1;",
                [ct, cn]))

        # Filtro por fecha (año)
        for c in fecha:
            pares.append(_par(e, "facil",
                f"¿Cuántos registros de {t.nombre} tienen {c.comentario or c.nombre} "
                f"en el año 2024?",
                f"SELECT COUNT(*) FROM {t.nombre} WHERE YEAR({c.nombre}) = 2024;",
                ["COUNT(*)"]))
    return pares


# --------------------------------------------------------------------------
# Nivel MEDIA — JOIN, GROUP BY, HAVING
# --------------------------------------------------------------------------
def _relaciones(e: Esquema):
    """Devuelve (tabla_hija, col_fk, tabla_padre, col_pk) por cada FK."""
    por_nombre = {t.nombre: t for t in e.tablas}
    rels = []
    for t in e.tablas:
        for c in t.columnas:
            if c.fk:
                padre, colpk = c.fk.split(".")
                if padre in por_nombre:
                    rels.append((t, c.nombre, por_nombre[padre], colpk))
    return rels


def _medias(e: Esquema):
    pares = []
    # GROUP BY sobre una tabla: conteo y agregación por categoría
    for t in e.tablas:
        for cat in _cols(t, "categoria"):
            pares.append(_par(e, "media",
                f"¿Cuántos registros de {t.nombre} hay por cada "
                f"{cat.comentario or cat.nombre}?",
                f"SELECT {cat.nombre}, COUNT(*) FROM {t.nombre} "
                f"GROUP BY {cat.nombre};", [cat.nombre, "COUNT(*)"]))
            for num in _cols(t, "numero"):
                pares.append(_par(e, "media",
                    f"¿Cuál es el promedio de {num.comentario or num.nombre} "
                    f"por {cat.comentario or cat.nombre} en {t.nombre}?",
                    f"SELECT {cat.nombre}, AVG({num.nombre}) FROM {t.nombre} "
                    f"GROUP BY {cat.nombre};", [cat.nombre, f"AVG({num.nombre})"]))
                pares.append(_par(e, "media",
                    f"¿Cuál es la suma de {num.comentario or num.nombre} "
                    f"por {cat.comentario or cat.nombre} en {t.nombre}?",
                    f"SELECT {cat.nombre}, SUM({num.nombre}) FROM {t.nombre} "
                    f"GROUP BY {cat.nombre};", [cat.nombre, f"SUM({num.nombre})"]))
                # HAVING
                pares.append(_par(e, "media",
                    f"¿Qué {cat.comentario or cat.nombre} de {t.nombre} tienen un "
                    f"promedio de {num.comentario or num.nombre} mayor a 0? "
                    f"Devuelve {cat.nombre} y el promedio.",
                    f"SELECT {cat.nombre}, AVG({num.nombre}) FROM {t.nombre} "
                    f"GROUP BY {cat.nombre} HAVING AVG({num.nombre}) > 0;",
                    [cat.nombre, f"AVG({num.nombre})"]))

    # JOIN de tablas relacionadas
    for (hija, fk, padre, pk) in _relaciones(e):
        txt_padre = _cols(padre, "texto")
        txt_hija = _cols(hija, "texto")
        num_hija = _cols(hija, "numero")
        # JOIN simple: listar hija con atributo de padre
        if txt_padre:
            cp = txt_padre[0].nombre
            cols_h = (txt_hija[0].nombre if txt_hija else
                      [c.nombre for c in hija.columnas if c.pk][0])
            pares.append(_par(e, "media",
                f"Muestra {cols_h} de {hija.nombre} junto con {cp} de {padre.nombre}.",
                f"SELECT h.{cols_h}, p.{cp} FROM {hija.nombre} h "
                f"JOIN {padre.nombre} p ON h.{fk} = p.{pk};", [cols_h, cp]))
            # JOIN + GROUP BY: conteo de hija por atributo de padre
            pares.append(_par(e, "media",
                f"¿Cuántos registros de {hija.nombre} hay por cada {cp} de "
                f"{padre.nombre}? Devuelve {cp} y el conteo.",
                f"SELECT p.{cp}, COUNT(*) FROM {hija.nombre} h "
                f"JOIN {padre.nombre} p ON h.{fk} = p.{pk} GROUP BY p.{cp};",
                [cp, "COUNT(*)"]))
            # JOIN + SUM de medida de hija por padre
            if num_hija:
                cn = num_hija[0].nombre
                pares.append(_par(e, "media",
                    f"¿Cuál es la suma de {num_hija[0].comentario or cn} de "
                    f"{hija.nombre} por cada {cp} de {padre.nombre}? "
                    f"Devuelve {cp} y la suma.",
                    f"SELECT p.{cp}, SUM(h.{cn}) FROM {hija.nombre} h "
                    f"JOIN {padre.nombre} p ON h.{fk} = p.{pk} GROUP BY p.{cp};",
                    [cp, f"SUM(h.{cn})"]))
    return pares


# --------------------------------------------------------------------------
# Nivel DIFÍCIL — subconsultas, WITH, funciones de ventana, fechas
# --------------------------------------------------------------------------
def _dificiles(e: Esquema):
    pares = []
    for t in e.tablas:
        num = _cols(t, "numero")
        cat = _cols(t, "categoria")
        txt = _cols(t, "texto")
        fecha = _cols(t, "fecha")
        pk = [c.nombre for c in t.columnas if c.pk]
        col_ret = txt[0].nombre if txt else (pk[0] if pk else t.columnas[0].nombre)

        # Subconsulta: filas por encima del promedio
        for c in num:
            pares.append(_par(e, "dificil",
                f"Muestra los registros de {t.nombre} cuyo "
                f"{c.comentario or c.nombre} es mayor al promedio de "
                f"{c.comentario or c.nombre}. Devuelve {col_ret} y {c.nombre}.",
                f"SELECT {col_ret}, {c.nombre} FROM {t.nombre} "
                f"WHERE {c.nombre} > (SELECT AVG({c.nombre}) FROM {t.nombre});",
                [col_ret, c.nombre]))

        # WITH (CTE) + agregación por categoría, filtrando por el máximo
        if cat and num:
            cc, cn = cat[0].nombre, num[0].nombre
            pares.append(_par(e, "dificil",
                f"Usando una CTE, calcula la suma de {num[0].comentario or cn} por "
                f"{cat[0].comentario or cc} en {t.nombre} y devuelve la "
                f"{cat[0].comentario or cc} con la suma más alta. "
                f"Devuelve {cc} y el total.",
                f"WITH totales AS (SELECT {cc} AS g, SUM({cn}) AS total "
                f"FROM {t.nombre} GROUP BY {cc}) "
                f"SELECT g, total FROM totales "
                f"ORDER BY total DESC LIMIT 1;", ["g", "total"]))

        # Función de ventana: ranking por categoría
        if cat and num and txt:
            cc, cn, ct = cat[0].nombre, num[0].nombre, txt[0].nombre
            pares.append(_par(e, "dificil",
                f"Para cada {cat[0].comentario or cc} en {t.nombre}, asigna un "
                f"ranking de {ct} según {num[0].comentario or cn} de mayor a menor. "
                f"Devuelve {ct}, {cc}, {cn} y el ranking.",
                f"SELECT {ct}, {cc}, {cn}, "
                f"RANK() OVER (PARTITION BY {cc} ORDER BY {cn} DESC) AS ranking "
                f"FROM {t.nombre};", [ct, cc, cn, "ranking"]))

        # Fechas: agregación por año
        for c in fecha:
            pares.append(_par(e, "dificil",
                f"¿Cuántos registros de {t.nombre} hay por año según "
                f"{c.comentario or c.nombre}? Devuelve el año y el conteo, "
                f"ordenado por año.",
                f"SELECT YEAR({c.nombre}) AS anio, COUNT(*) AS n "
                f"FROM {t.nombre} GROUP BY YEAR({c.nombre}) ORDER BY anio;",
                ["anio", "n"]))
            if num:
                cn = num[0].nombre
                pares.append(_par(e, "dificil",
                    f"¿Cuál es la suma de {num[0].comentario or cn} por mes del año "
                    f"2024 en {t.nombre}, según {c.comentario or c.nombre}? "
                    f"Devuelve el mes y la suma, ordenado por mes.",
                    f"SELECT MONTH({c.nombre}) AS mes, SUM({cn}) AS total "
                    f"FROM {t.nombre} WHERE YEAR({c.nombre}) = 2024 "
                    f"GROUP BY MONTH({c.nombre}) ORDER BY mes;", ["mes", "total"]))

    # Difícil con JOIN + subconsulta correlacionada ligera
    for (hija, fk, padre, pk) in _relaciones(e):
        num_hija = _cols(hija, "numero")
        txt_padre = _cols(padre, "texto")
        if num_hija and txt_padre:
            cn, cp = num_hija[0].nombre, txt_padre[0].nombre
            pares.append(_par(e, "dificil",
                f"Muestra el {cp} de {padre.nombre} cuya suma de "
                f"{num_hija[0].comentario or cn} en {hija.nombre} es la mayor. "
                f"Devuelve {cp} y el total.",
                f"WITH agg AS (SELECT h.{fk} AS k, SUM(h.{cn}) AS total "
                f"FROM {hija.nombre} h GROUP BY h.{fk}) "
                f"SELECT p.{cp}, a.total FROM agg a "
                f"JOIN {padre.nombre} p ON a.k = p.{pk} "
                f"ORDER BY a.total DESC LIMIT 1;", [cp, "total"]))
    return pares


# --------------------------------------------------------------------------
# Paráfrasis para diversificar las preguntas (misma SQL)
# --------------------------------------------------------------------------
_PREFIJOS = [
    "", "Por favor, ", "Necesito saber: ", "Consulta: ", "Dime ",
    "Quisiera saber ", "Ayúdame a obtener ", "Me gustaría saber ",
    "Obtén ", "Calcula: ", "Reporta ",
]


def _cuerpo_minuscula(pregunta: str) -> str:
    """Prepara el cuerpo para anteponer un prefijo, leyendo bien en español.

    Quita '¿'/'?' iniciales y finales y pasa la primera letra a minúscula, de
    modo que 'Ayúdame a obtener ' + cuerpo quede natural.
    """
    p = pregunta.strip()
    if p.startswith("¿") and p.endswith("?"):
        p = p[1:-1]
    if p and p[0].isalpha():
        p = p[0].lower() + p[1:]
    return p


def _parafrasear(par, n_variantes=2, rng=None):
    rng = rng or random
    base = [par]
    cuerpo = _cuerpo_minuscula(par["pregunta"])
    opciones = rng.sample(_PREFIJOS[1:], k=min(n_variantes, len(_PREFIJOS) - 1))
    for pref in opciones:
        nueva = dict(par)
        nueva["pregunta"] = pref + cuerpo
        base.append(nueva)
    return base


# --------------------------------------------------------------------------
# API pública
# --------------------------------------------------------------------------
def generar_para_esquema(e: Esquema, con_parafrasis=True, semilla=2026):
    rng = random.Random(semilla + hash(e.nombre) % 1000)
    pares = _faciles(e) + _medias(e) + _dificiles(e)
    if con_parafrasis:
        # Más variantes en media/difícil para equilibrar la distribución por
        # nivel (esos niveles pesan más en EX y hay menos plantillas base).
        variantes = {"facil": 3, "media": 6, "dificil": 7}
        expandido = []
        for p in pares:
            expandido.extend(
                _parafrasear(p, n_variantes=variantes[p["nivel"]], rng=rng))
        pares = expandido
    for p in pares:
        p["ddl"] = ddl_esquema(e)
    return pares


def generar_entrenamiento(con_parafrasis=True):
    todos = []
    for e in ESQUEMAS_ENTRENAMIENTO:
        todos.extend(generar_para_esquema(e, con_parafrasis))
    return todos


def generar_validacion_sintetica(con_parafrasis=False):
    """Pares sobre los esquemas de validación (referencia para el harness)."""
    todos = []
    for e in ESQUEMAS_VALIDACION:
        todos.extend(generar_para_esquema(e, con_parafrasis))
    return todos


if __name__ == "__main__":
    tr = generar_entrenamiento()
    va = generar_validacion_sintetica()
    from collections import Counter
    print("Entrenamiento:", len(tr), "pares")
    print("  por nivel:", dict(Counter(p["nivel"] for p in tr)))
    print("Validación sintética:", len(va), "pares")
    print("  por nivel:", dict(Counter(p["nivel"] for p in va)))
