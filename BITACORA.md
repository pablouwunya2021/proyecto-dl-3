# Bitácora del proyecto

| # | Fecha | Autor | Actividad |
|---|-------|-------|-----------|
| 1 | 2026-10-13 | Pablo | Diseño de los 10 esquemas propios (DDL con COMMENT) y los 2 de validación. |
| 2 | 2026-10-14 | Luis Palacios | Generador de pares pregunta–SQL por nivel (fácil/media/difícil). |
| 3 | 2026-10-15 | Pablo | Validación de pares en MySQL 8.4.10 y registro de descartes. |
| 4 | 2026-10-16 | Luis Palacios | Prompt compartido e implementación de `solucion.py` (contrato). |
| 5 | 2026-10-18 | Pablo | Script de entrenamiento LoRA/QLoRA; prueba de la config A (r=8). |
| 6 | 2026-10-20 | Luis Palacios | Config B (r=32); registro de curvas de loss y tiempos. |
| 7 | 2026-10-22 | Pablo | Harness de EX; baseline y evaluación de adapters. |
| 8 | 2026-10-23 | Luis Palacios | Experimento de inferencia (auto-corrección) y análisis de errores. |
| 9 | 2026-10-24 | Pablo y Luis Palacios | Predicción de EX, presentación y revisión final. |
| 10 | 2026-10-25 | Luis Palacios | Entrenamiento en Colab T4 de configs A (r=8) y B (r=32), 100 pasos (~0.8 épocas); adapter de entrega, presentación y documentación final. |

## Notas por entrada

- **2026-10-13 — Pablo:** 10 esquemas propios mezclando español e inglés y nombres abreviados (hr, fleet, clinic) porque la evaluación oculta puede usar ambos idiomas y abreviaturas.
- **2026-10-14 — Luis Palacios:** Plantillas por nivel (fácil/media/difícil) que producen SQL a partir del esquema; todo SQL se ejecuta en MySQL antes de conservarse.
- **2026-10-15 — Pablo:** Se conservaron 2,099 pares (1,024 fáciles, 539 medios, 536 difíciles).
- **2026-10-16 — Luis Palacios:** Prompt compartido entre entrenamiento e inferencia (src/prompt.py); greedy (do_sample=False), semilla 2026, filtro de solo lectura.
- **2026-10-18 — Pablo:** Hipótesis A: r=8 basta para aprender el formato y patrones SQL, entrenando más rápido.
- **2026-10-20 — Luis Palacios:** Hipótesis B: r=32 da más capacidad para consultas difíciles (subconsultas, ventanas).
- **2026-10-22 — Pablo:** Harness de EX ponderada con las reglas del evaluador (orden opcional, 2 decimales, columna extra no penaliza).
- **2026-10-23 — Luis Palacios:** Auto-corrección con ejecutar: ante error de MySQL se regenera con el error como pista (máx. 3 llamadas).
- **2026-10-24 — ambos:** Predicción de EX documentada en presentacion.pdf.
- **2026-10-25 — Luis Palacios:** Entrenamiento de A y B en Colab T4 (LoRA fp16, 100 pasos con batch 2x8; bitsandbytes no cargó en el CUDA de Colab, así que se descartó QLoRA); se copió el mejor adapter a `adapter/` y se generó la presentación.
