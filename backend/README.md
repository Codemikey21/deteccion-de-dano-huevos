# Egg Detection API (FastAPI)

Backend de inferencia para detección de huevos y grietas con **YOLOv8n @ imgsz=960**.

## Propósito

- Recibir una imagen (JPEG/PNG)
- Ejecutar inferencia con el checkpoint seleccionado (`yolov8n_960`)
- Devolver detecciones (`egg`, `crack`) con bounding boxes
- Clasificar operativamente: `approved` / `rejected` / `unknown`

**Limitación:** `approved` significa solo *huevo detectado sin grieta visible según este modelo*.
No evalúa suciedad, peso, calibre comercial ni defectos fuera de INDIGO.

## Arquitectura

```text
backend/app/
├── main.py              # FastAPI + CORS + lifespan
├── api/routes/          # /health, /predict
├── core/                # config, constants
├── schemas/             # Pydantic response models
└── services/
    ├── inference.py     # Carga YOLO (singleton)
    └── classification.py # approved / rejected / unknown
```

## Requisitos previos

1. Python 3.10+
2. Copiar manualmente `best.pt` desde Google Drive:

   `egg-detection/runs/yolov8n_960/weights/best.pt` → `backend/models/best.pt`

3. Ver [`models/README.md`](models/README.md)

## Instalación

Desde la **raíz del repositorio**:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
```

## Ejecutar servidor

Desde la **raíz del repositorio**:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Probar `/predict`

```bash
curl -X POST "http://127.0.0.1:8000/predict" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@ruta/a/imagen.jpg"
```

O subir imagen desde `/docs` → **POST /predict**.

## Variables de entorno

| Variable | Default | Descripción |
| --- | --- | --- |
| `MODEL_PATH` | `backend/models/best.pt` | Checkpoint YOLO |
| `MODEL_CONFIDENCE` | `0.25` | Confianza mínima inferencia (inicial, configurable) |
| `CRACK_CONFIDENCE` | `0.25` | Umbral crack para `rejected` (inicial, configurable) |
| `CORS_ORIGINS` | `*` | Orígenes CORS (`*` solo desarrollo / Expo) |

## Tests

```bash
python -m pytest backend/tests -q
```

Los tests de clasificación **no requieren** `best.pt`.

## Preparación futura

- **Expo / React Native:** consumir `POST /predict` con multipart
- **AWS EC2:** desplegar con uvicorn/gunicorn, restringir `CORS_ORIGINS`, montar `best.pt`
