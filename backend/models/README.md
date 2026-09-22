# Checkpoint del modelo

Coloca aquí manualmente el archivo **`best.pt`** del experimento seleccionado:

| Origen (Google Drive) | Destino local |
| --- | --- |
| `egg-detection/runs/yolov8n_960/weights/best.pt` | `backend/models/best.pt` |

## Modelo seleccionado

- **YOLOv8n** entrenado con `imgsz=960` (experimento `yolov8n_960`)
- Clases: `0=egg`, `1=crack`

## Importante

- **No versionar** archivos `.pt` en Git.
- El backend no descarga el checkpoint automáticamente.
- Sin `best.pt`, `/health` responde con `model_loaded=false` y `/predict` devuelve HTTP 503.

Configura la ruta con la variable de entorno `MODEL_PATH` si usas otra ubicación.
