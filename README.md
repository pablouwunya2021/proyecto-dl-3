# Proyecto 3 — Text-to-SQL con fine-tuning LoRA

Fine-tuning con LoRA de **Qwen2.5-Coder-1.5B-Instruct** para que, dado el
esquema de una base de datos (sentencias `CREATE TABLE`) y una pregunta en
español, genere una consulta **MySQL 8.4** correcta.

Universidad del Valle · Deep Learning 2026 · Modalidad parejas.

---

## Estructura del repositorio

```
solucion.py            Contrato de entrega: generar_sql(esquema, pregunta, ejecutar)
config.json            modelo_base, adapter, usar_adapter, semilla
requirements.txt       Dependencias fijadas (probadas para Colab T4)
adapter/               Adapter LoRA entrenado (se genera en el notebook 02)
src/
  prompt.py            Prompt compartido entre entrenamiento e inferencia
  sql_utils.py         Extracción y validación (solo lectura) del SQL
  esquemas.py          10 esquemas de entrenamiento + 2 de validación
  generar_datos.py     Generador de pares pregunta–SQL por nivel
  exportar_datos.py    Materializa train.jsonl y validacion_propia.csv
  validar_mysql.py     Ejecuta cada par en MySQL 8.4.10 y filtra descartes
  entrenar.py          Fine-tuning LoRA/QLoRA (configs A y B)
  evaluar.py           Harness de EX ponderada (reglas del evaluador oculto)
  convertir_spider.py  (Opcional) complemento con datos públicos
esquemas/              Volcado .sql de cada esquema (DDL + datos de ejemplo)
datos/
  entrenamiento/       train.jsonl, resumen.json
  validacion/          validacion_propia.csv / .jsonl (2 esquemas nuevos, 40 preg.)
  descartes/           descartes.csv (pares que no ejecutaron en MySQL)
notebooks/
  01_datos.ipynb       Generar + validar + exportar el dataset
  02_entrenamiento.ipynb  Entrenar configs A y B, curvas de loss
  03_evaluacion.ipynb  Baseline, adapters, experimento de inferencia, errores
resultados/
  validacion_propia.csv   EX por configuración
BITACORA.md, CONTRIBUCIONES.md, historial_git.txt, presentacion.pdf
```

---

## Cómo se ejecuta la entrega (lo que corre el docente)

El evaluador instala `requirements.txt` en Colab (GPU T4) y usa:

```python
import json, solucion
sql = solucion.generar_sql(esquema, pregunta, ejecutar)   # ejecutar es opcional
```

- `config.json` indica el modelo base y si se usa el adapter.
- Con `"usar_adapter": true` se carga el adapter de `adapter/`; con `false` se
  usa el modelo base con **el mismo prompt** (para medir el aporte del fine-tuning).
- Generación **determinista** (`do_sample=False`, semilla 2026).
- Devuelve **una sola** consulta `SELECT` o `WITH ... SELECT`, de solo lectura.

### Reproducir desde cero

1. **Datos** — `notebooks/01_datos.ipynb`: genera los pares, los valida en
   MySQL 8.4.10 y escribe `datos/entrenamiento/train.jsonl` (solo los que
   ejecutan sin error) y `datos/descartes/descartes.csv`.
2. **Entrenamiento** — `notebooks/02_entrenamiento.ipynb`: entrena el adapter A
   (r=8) y el B (r=32), guarda reportes y curvas de loss.
3. **Evaluación** — `notebooks/03_evaluacion.ipynb`: baseline, adapters,
   experimento de auto-corrección y análisis de errores.
4. Copia el mejor adapter a `adapter/` para la entrega:
   `rm -rf adapter && cp -r adapter_B adapter` (o `adapter_A`).

### MySQL 8.4.10

```bash
docker run -d --name mysql84 -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.4.10
pip install pymysql
```

Config por defecto (incluye `ONLY_FULL_GROUP_BY`), tal como la evaluación oculta.

---

## Dataset

- **≥ 2,000 pares** generados sobre **10 esquemas propios** (español e inglés,
  nombres abreviados), en tres niveles: fácil (1 tabla), media (JOIN/GROUP BY/
  HAVING), difícil (subconsultas, WITH, funciones de ventana, fechas).
- Todos los pares se **validan en MySQL 8.4.10**; solo se conservan los que
  ejecutan sin error. Los descartes se registran en `datos/descartes/`.
- Partición **por esquema**: los 2 esquemas de validación (`aerolinea`, `banco`)
  **no** aparecen en el entrenamiento.
- (Opcional) `src/convertir_spider.py` añade datos públicos de Spider traducidos.

## Experimentos

- **Baseline:** modelo base sin adapter, mismo prompt.
- **Dos configuraciones LoRA** que difieren en un solo factor (rank `r`):
  A (r=8) vs B (r=32). Hipótesis y resultados en el notebook 02 y la presentación.
- **Experimento de inferencia:** auto-corrección de la consulta usando `ejecutar`
  (hasta 3 llamadas): si MySQL devuelve error, se reintenta con el error como
  pista. Implementado en `solucion.py` y evaluado en el notebook 03.

---

## Licencias

- **Modelo base:** Qwen2.5-Coder-1.5B-Instruct — licencia Apache 2.0 (Alibaba/Qwen).
- **Spider** (si se usa): licencia CC BY-SA 4.0.
- **Código de este repositorio:** uso académico para el curso.

## Uso de IA

Se utilizó un asistente de IA (Claude) como apoyo para **estructurar el
repositorio, redactar el pipeline de datos, el entrenamiento y el harness de
evaluación**. El diseño de esquemas, las hipótesis de los experimentos, la
ejecución del entrenamiento en GPU, la revisión del dataset y el análisis de
resultados son responsabilidad de la pareja. Todo el código fue revisado y
probado por los integrantes. No se usan APIs externas al generar las consultas
(solo el modelo base + adapter local), como exige el enunciado.
