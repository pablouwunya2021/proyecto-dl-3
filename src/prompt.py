"""Construcción del prompt para Text-to-SQL.

Este módulo es la ÚNICA fuente de verdad del formato del prompt. Tanto el
entrenamiento (notebooks/scripts) como la inferencia (solucion.py) importan de
aquí, de modo que el prompt con el que se entrena el adapter sea idéntico al
prompt con el que se genera en evaluación. Si cambian el prompt, re-entrenen.

El mensaje se arma como un chat (system + user) y se renderiza con el
chat_template del tokenizer de Qwen. La respuesta esperada del modelo es una
única consulta SQL (SELECT o WITH ... SELECT), sin explicaciones ni markdown.
"""

SYSTEM_PROMPT = (
    "Eres un experto en MySQL 8.4. Dada el esquema de una base de datos "
    "(sentencias CREATE TABLE) y una pregunta en español, escribes UNA sola "
    "consulta MySQL que la responde.\n"
    "Reglas estrictas:\n"
    "- Devuelve únicamente la consulta SQL, sin explicación ni comentarios ni "
    "bloques de código markdown.\n"
    "- Usa solo tablas y columnas que existan en el esquema.\n"
    "- La consulta debe ser de solo lectura: SELECT o WITH ... SELECT. Nunca "
    "INSERT, UPDATE, DELETE, DROP ni DDL.\n"
    "- Respeta ONLY_FULL_GROUP_BY: toda columna no agregada del SELECT debe "
    "estar en el GROUP BY.\n"
    "- Devuelve exactamente las columnas que pide la pregunta.\n"
    "- Termina la consulta con punto y coma."
)


def construir_mensajes(esquema: str, pregunta: str):
    """Devuelve la lista de mensajes [system, user] para el chat_template."""
    user = (
        "### Esquema de la base de datos (MySQL):\n"
        f"{esquema.strip()}\n\n"
        "### Pregunta (español):\n"
        f"{pregunta.strip()}\n\n"
        "### Consulta MySQL:"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def construir_prompt(tokenizer, esquema: str, pregunta: str) -> str:
    """Renderiza el prompt listo para generar (add_generation_prompt=True)."""
    mensajes = construir_mensajes(esquema, pregunta)
    return tokenizer.apply_chat_template(
        mensajes,
        tokenize=False,
        add_generation_prompt=True,
    )


def construir_ejemplo_entrenamiento(tokenizer, esquema: str, pregunta: str, sql: str) -> str:
    """Texto completo (prompt + respuesta) para entrenamiento causal.

    La respuesta del asistente es la consulta SQL objetivo. Se usa el mismo
    chat_template; el entrenamiento enmascara el prompt y solo computa loss
    sobre la respuesta (ver notebooks/scripts de entrenamiento).
    """
    mensajes = construir_mensajes(esquema, pregunta)
    mensajes.append({"role": "assistant", "content": sql.strip()})
    return tokenizer.apply_chat_template(
        mensajes,
        tokenize=False,
        add_generation_prompt=False,
    )
