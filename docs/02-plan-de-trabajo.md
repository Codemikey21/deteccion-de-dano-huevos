# Plan de trabajo

El proyecto avanza por fases. Cada fase crea únicamente las carpetas y dependencias que
necesita, de modo que el historial de commits refleje el avance real del trabajo.

> **Este documento es planificación.** Salvo la Fase 0, ninguna de las fases descritas está
> implementada todavía: no hay conjunto de datos, ni modelo entrenado, ni aplicación. Cada
> fase se desarrollará mediante commits pequeños y coherentes, y su contenido podrá ajustarse
> según lo que se encuentre al avanzar.

---

## Fases

### Fase 0 — Preparación del repositorio *(actual)*

Estructura base, documentación del alcance y configuración de Git.

Se crea: `data/raw/`, `data/processed/`, `docs/`, `README.md`, `requirements.txt`,
`.gitignore`, `.gitattributes`, `.env.example`.

### Fase 1 — Construcción del conjunto de datos

Captura de imágenes de huevos con la cámara y organización del material recolectado.

Se crea: `scripts/` (utilidades de captura y de organización de imágenes).
Se agrega a `requirements.txt`: ya cubierto (OpenCV, NumPy).

### Fase 2 — Etiquetado y preparación de datos

Validación previa de las categorías de tipo (ver
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md), sección 3b): no se puede etiquetar
hasta saber si "Triple A", "criollo" y "semicriollo" pertenecen al mismo eje de clasificación.
Definido el esquema de etiquetas, se etiqueta por estado y por tipo y se exportan las
particiones de entrenamiento, validación y prueba.

Se crea: `data/train/`, `data/validation/`, `data/test/`.

### Fase 3 — Exploración y análisis del conjunto de datos

Conteo de imágenes por clase, revisión del balance entre clases y análisis de las
características de las imágenes.

Se crea: `notebooks/`.
Se agrega a `requirements.txt`: `pandas`, `matplotlib`, `seaborn`.

### Fase 4 — Entrenamiento del modelo

Selección de la librería y de la arquitectura —decisión pendiente, ver
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md), sección 8—, entrenamiento y
guardado de los pesos.

Se crea: `training/`, `models/`.
Se agrega a `requirements.txt`: la librería de aprendizaje profundo que se seleccione y
`scikit-learn` para el cálculo de métricas.

### Fase 5 — Evaluación

Métricas sobre el conjunto de prueba, matriz de confusión y análisis de errores.

Se crea: `evaluation/`.

### Fase 6 — Inferencia en tiempo real

Detección y clasificación sobre el flujo de video en vivo.

Se crea: `src/` (módulos de inferencia y procesamiento en tiempo real) y `tests/`.
Se agrega a `requirements.txt`: `pytest`.

### Fase 7 — Backend

API que recibe los cuadros de video y devuelve las predicciones.

Se crea: `backend/`.
Se agrega a `requirements.txt`: `fastapi`, `uvicorn`, `python-multipart`.

### Fase 8 — Frontend

Interfaz web que muestra el video y los resultados de la clasificación.

Se crea: `frontend/`.

### Fase 9 — Despliegue en AWS

Despliegue en una instancia EC2 del AWS Academy Learner Lab y documentación del
procedimiento para recrearlo.

Se crea: `deploy/` y `docs/03-despliegue.md`.

---

## Estructura objetivo

Así quedará el repositorio al finalizar todas las fases. Es la misma estructura publicada en
el [`README.md`](../README.md); ambas listas deben mantenerse sincronizadas.

```
deteccion-de-dano-huevos/
├── data/              # Conjuntos de datos (contenido no versionado)
│   ├── raw/           # Imágenes originales tal como se capturaron
│   ├── processed/     # Imágenes ya preparadas
│   ├── train/         # Partición de entrenamiento
│   ├── validation/    # Partición de validación
│   └── test/          # Partición de prueba
├── notebooks/         # Análisis exploratorio
├── training/          # Scripts de entrenamiento
├── models/            # Modelos entrenados (contenido no versionado)
├── evaluation/        # Métricas y análisis de resultados
├── src/               # Módulos de inferencia y procesamiento en tiempo real
├── backend/           # API
├── frontend/          # Interfaz web
├── scripts/           # Utilidades de apoyo
├── tests/             # Pruebas automatizadas
├── deploy/            # Configuración y documentación de despliegue
└── docs/              # Documentación
```

Fase en la que se crea cada carpeta:

| Carpeta | Fase |
| --- | --- |
| `data/raw/`, `data/processed/`, `docs/` | 0 (existen) |
| `scripts/` | 1 |
| `data/train/`, `data/validation/`, `data/test/` | 2 |
| `notebooks/` | 3 |
| `training/`, `models/` | 4 |
| `evaluation/` | 5 |
| `src/`, `tests/` | 6 |
| `backend/` | 7 |
| `frontend/` | 8 |
| `deploy/` | 9 |

---

## Convención de commits

Se usa [Conventional Commits](https://www.conventionalcommits.org/) para mantener un
historial legible:

| Prefijo | Uso |
| --- | --- |
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un error |
| `docs` | Documentación |
| `chore` | Configuración, estructura, dependencias |
| `refactor` | Reorganización de código sin cambio de comportamiento |
| `test` | Pruebas |

Los commits deben ser pequeños y describir un solo cambio.
