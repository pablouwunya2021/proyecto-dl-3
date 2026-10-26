# Contribuciones

## Responsables por área

| Área | Responsable |
|------|-------------|
| Datos (esquemas, generación, validación en MySQL, descartes) | Pablo |
| Entrenamiento (LoRA configs A/B, curvas, selección de adapter) | Luis Palacios |
| Validación y errores (harness EX, baseline, inferencia, análisis) | Pablo / Luis Palacios |

## Tabla de tareas

| Tarea | Responsable | Evidencia (commit / archivo) |
|-------|-------------|------------------------------|
| Diseño de 10 esquemas propios + 2 de validación | Pablo | `src/esquemas.py`, `esquemas/` |
| Generador de pares por nivel | Luis Palacios | `src/generar_datos.py` |
| Validación en MySQL 8.4.10 y descartes | Pablo | `src/validar_mysql.py`, `datos/descartes/descartes.csv` |
| Prompt compartido y `solucion.py` | Luis Palacios | `src/prompt.py`, `solucion.py` |
| Entrenamiento LoRA (config A, r=8) | Pablo | `src/entrenar.py`, `adapter_A/reporte_entrenamiento.json` |
| Entrenamiento LoRA (config B, r=32) | Luis Palacios | `adapter_B/reporte_entrenamiento.json` |
| Harness de EX y baseline | Pablo | `src/evaluar.py`, `resultados/detalle_baseline.csv` |
| Experimento de inferencia (auto-corrección) | Luis Palacios | `solucion.py`, `resultados/detalle_mejor_autocorreccion.csv` |
| Análisis de errores por categoría | Pablo / Luis Palacios | `notebooks/03_evaluacion.ipynb` |
| Presentación y predicción de EX | Luis Palacios | `presentacion.pdf`, `src/presentacion.py` |

