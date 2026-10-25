# Carpeta del adapter de entrega

Aquí va el **adapter LoRA entrenado** que se entrega. Está vacía hasta que
ejecuten el entrenamiento.

Tras entrenar y evaluar (notebooks 02 y 03), copien el mejor adapter aquí:

```bash
rm -rf adapter && cp -r adapter_B adapter   # o adapter_A, según el EX
```

El archivo `config.json` de la raíz debe apuntar a esta carpeta
(`"adapter": "adapter/"`, `"usar_adapter": true`).

Contenido esperado después de copiar:
`adapter_config.json`, `adapter_model.safetensors`, archivos del tokenizer y
`reporte_entrenamiento.json`.
