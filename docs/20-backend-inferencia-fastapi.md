# Backend de inferencia — FastAPI

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`19-seleccion-modelo-final.md`](19-seleccion-modelo-final.md) ·
[`18-experimento-yolov8n-960.md`](18-experimento-yolov8n-960.md)

> **Estado: BACKEND IMPLEMENTADO — PENDIENTE DE PRUEBA CON CHECKPOINT REAL**
>
> El código está listo; falta colocar `backend/models/best.pt` y validar inferencia end-to-end.

---

## Objetivo

Exponer un API HTTP que:

1. Cargue **YOLOv8n @ imgsz=960** (`yolov8n_960/best.pt`)
2. Reciba imágenes JPEG/PNG
3. Devuelva detecciones `egg` / `crack` con bbox y confidence
4. Clasifique: **approved** / **rejected** / **unknown**
5. Prepare integración futura con **React Native + Expo** y despliegue en **AWS EC2**

---

## Modelo utilizado

| Campo | Valor |
| --- | --- |
| Arquitectura | YOLOv8n |
| imgsz | 960 |
| Checkpoint | `runs/yolov8n_960/weights/best.pt` |
| Clases | 0=egg, 1=crack |

Ubicación local esperada: `backend/models/best.pt` (copia manual desde Drive).

---

## Arquitectura

```text
backend/app/
├── main.py                 # FastAPI, CORS, lifespan (carga modelo)
├── api/routes/
│   ├── health.py           # GET /health
│   └── predict.py          # POST /predict
├── core/
│   ├── config.py           # pydantic-settings (.env)
│   └── constants.py
├── schemas/prediction.py   # Pydantic models
└── services/
    ├── inference.py        # YOLO singleton
    └── classification.py   # Lógica approved/rejected/unknown
```

---

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/` | Info API + link a `/docs` |
| GET | `/health` | Estado servicio y `model_loaded` (sin inferencia) |
| POST | `/predict` | Inferencia multipart `file` |
| GET | `/docs` | Swagger UI |

---

## Flujo de inferencia

1. Cliente envía `multipart/form-data` con campo `file`
2. Validación: MIME (`image/jpeg`, `image/png`), no vacío, decodificable (Pillow)
3. YOLO predict (`imgsz=960`, `conf=MODEL_CONFIDENCE`, `verbose=False`, sin guardar runs)
4. Clasificación sobre detecciones (`CRACK_CONFIDENCE` para crack válido)
5. Respuesta JSON con status, route, reason, detections, inference_ms

---

## Lógica approved / rejected / unknown

| Condición | status | route | reason |
| --- | --- | --- | --- |
| Crack con conf ≥ `CRACK_CONFIDENCE` | rejected | reject | crack_detected |
| Egg detectado, sin crack válido | approved | accept | no_crack_detected |
| Sin egg detectado | unknown | review | egg_not_detected |

**Importante:** `approved` **no** implica calidad comercial completa. Solo indica que el
modelo no detectó grieta visible. No identifica suciedad, peso, calibre Triple A, criollo,
semicriollo u otros defectos ausentes en INDIGO.

---

## Configuración

Archivo: `backend/.env` (plantilla: `backend/.env.example`)

| Variable | Default | Notas |
| --- | --- | --- |
| `MODEL_PATH` | `backend/models/best.pt` | Checkpoint local |
| `MODEL_CONFIDENCE` | 0.25 | Umbral inferencia YOLO — **valor inicial configurable** |
| `CRACK_CONFIDENCE` | 0.25 | Umbral crack para rechazo — **valor inicial configurable** |
| `CORS_ORIGINS` | `*` | Desarrollo/Expo; restringir en producción |

---

## Ejecución local

```bash
# Desde raíz del repo
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Tests sin checkpoint:

```bash
python -m pytest backend/tests -q
```

---

## Limitaciones actuales

1. Requiere copia manual de `best.pt`
2. Umbrales 0.25 no optimizados científicamente — configurables
3. Sin autenticación ni rate limiting
4. CORS `*` documentado solo para desarrollo
5. Sin persistencia de imágenes de inferencia
6. Sin despliegue AWS ni app móvil en esta fase

---

## Preparación futura

### Expo / React Native

- `POST /predict` con `FormData` + campo `file`
- Configurar `CORS_ORIGINS` al origen de la app en producción

### AWS EC2

- Instalar dependencias, copiar `best.pt`, variables de entorno
- Servir con uvicorn/gunicorn detrás de reverse proxy
- Restringir CORS y firewall

---

## Estado

**BACKEND IMPLEMENTADO — PENDIENTE DE PRUEBA CON CHECKPOINT REAL**
