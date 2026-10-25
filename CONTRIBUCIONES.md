# Contribuciones

> **Completen con datos reales.** Cada integrante debe ser responsable de al
> menos una de estas áreas: **datos**, **entrenamiento**, o **validación y
> errores**. La evidencia debe poder rastrearse en los commits de cada cuenta.

## Responsables por área

| Área | Responsable |
|------|-------------|
| Datos (esquemas, generación, validación en MySQL, descartes) | [Integrante 1] |
| Entrenamiento (LoRA configs A/B, curvas, selección de adapter) | [Integrante 2] |
| Validación y errores (harness EX, baseline, inferencia, análisis) | [Integrante 1] / [Integrante 2] |

## Tabla de tareas

| Tarea | Responsable | Evidencia (commit / archivo) |
|-------|-------------|------------------------------|
| Diseño de 10 esquemas propios + 2 de validación | [Integrante 1] | `src/esquemas.py`, `esquemas/` |
| Generador de pares por nivel | [Integrante 2] | `src/generar_datos.py` |
| Validación en MySQL 8.4.10 y descartes | [Integrante 1] | `src/validar_mysql.py`, `datos/descartes/descartes.csv` |
| Prompt compartido y `solucion.py` | [Integrante 2] | `src/prompt.py`, `solucion.py` |
| Entrenamiento LoRA (config A, r=8) | [Integrante 1] | `src/entrenar.py`, `adapter_A/reporte_entrenamiento.json` |
| Entrenamiento LoRA (config B, r=32) | [Integrante 2] | `adapter_B/reporte_entrenamiento.json` |
| Harness de EX y baseline | [Integrante 1] | `src/evaluar.py`, `resultados/detalle_baseline.csv` |
| Experimento de inferencia (auto-corrección) | [Integrante 2] | `solucion.py`, `resultados/detalle_mejor_autocorreccion.csv` |
| Análisis de errores por categoría | [Integrante 1] / [Integrante 2] | `notebooks/03_evaluacion.ipynb` |
| Presentación y predicción de EX | ambos | `presentacion.pdf` |

> Reemplacen los nombres y añadan los hashes de commit reales como evidencia
> (`git log --oneline` por archivo). Recuerden: el repositorio debe tener
> commits de **ambas cuentas** (si no, la nota de colaboración es 0).
