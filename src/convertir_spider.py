"""(OPCIONAL) Convierte Spider a pares pregunta–SQL en español para MySQL.

El dataset sintético de src/generar_datos.py ya supera los 2,000 pares exigidos,
así que este script es un COMPLEMENTO para añadir diversidad con datos públicos
(Spider). Pasos que automatiza parcialmente:

1. Descarga Spider desde Hugging Face (`datasets`).
2. Toma pregunta (inglés) + SQL (dialecto SQLite) + esquema.
3. Traduce la pregunta al español (requiere un traductor; aquí se deja el
   gancho `traducir()` para que conecten su método — p.ej. un modelo local de
   traducción o reglas; NO usar APIs externas en inferencia, pero para preparar
   datos offline sí es válido).
4. Adapta el SQL a MySQL con reglas simples y marca para validación.

IMPORTANTE: todo par resultante DEBE pasar por src.validar_mysql antes de
entrenar. Spider usa SQLite; muchas consultas corren igual en MySQL, pero otras
no (comillas, LIMIT en subconsultas, funciones). Los que fallen se descartan.
"""
import re


def adaptar_sqlite_a_mysql(sql: str) -> str:
    """Reglas ligeras de adaptación de SQLite a MySQL 8.4."""
    s = sql.strip().rstrip(";")
    # Comillas dobles de identificadores/strings -> en MySQL las dobles son
    # identificadores; Spider suele usarlas para strings. Convertir a simples
    # cuando parezcan literales de texto.
    s = re.sub(r'"([^"]*)"', r"'\1'", s)
    # LIMIT con offset estilo "LIMIT 1 OFFSET 2" ya es válido en MySQL.
    # strftime -> DATE_FORMAT (caso común)
    s = s.replace("strftime('%Y',", "YEAR(").replace("strftime('%m',", "MONTH(")
    return s + ";"


def traducir(pregunta_en: str) -> str:
    """Gancho de traducción EN->ES. Conecten aquí su traductor offline.

    Ejemplos de opciones permitidas (offline, solo para preparar datos):
      - un modelo de traducción local (Helsinki-NLP/opus-mt-en-es) con transformers
      - traducción manual de una muestra
    Por defecto, lanza para que no se olviden de conectarlo.
    """
    raise NotImplementedError(
        "Conecta un traductor offline EN->ES (p.ej. Helsinki-NLP/opus-mt-en-es)."
    )


def cargar_spider(split="train", limite=None):
    """Devuelve pares crudos de Spider: [{pregunta_en, sql, db_id}]."""
    from datasets import load_dataset
    ds = load_dataset("spider", split=split)
    pares = []
    for i, ej in enumerate(ds):
        if limite and i >= limite:
            break
        pares.append({
            "pregunta_en": ej["question"],
            "sql": ej["query"],
            "db_id": ej["db_id"],
        })
    return pares


if __name__ == "__main__":
    print(__doc__)
    print("Este script es opcional. El dataset sintético ya cumple el mínimo.")
