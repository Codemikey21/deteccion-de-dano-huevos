# Plan de trabajo

El proyecto avanza por fases. Cada fase crea únicamente las carpetas y dependencias que
necesita, de modo que el historial de commits refleje el avance real del trabajo.

> **Este documento es planificación.** Está completada la Fase 0 y, de la Fase 1, únicamente su
> primer subpaso. Todo lo demás está pendiente: no hay conjunto de datos, ni modelo entrenado,
> ni aplicación. Cada fase se desarrollará mediante commits pequeños y coherentes, y su
> contenido podrá ajustarse según lo que se encuentre al avanzar.

---

## Fases

### Fase 0 — Preparación del repositorio *(completada)*

Estructura base, documentación del alcance y configuración de Git.

Se crea: `data/raw/`, `data/processed/`, `docs/`, `README.md`, `requirements.txt`,
`.gitignore`, `.gitattributes`, `.env.example`.

### Fase 1 — Estrategia y construcción del conjunto de datos *(en curso)*

**La captura de imágenes es un subpaso de esta fase, no toda la fase.** Antes de recolectar
material hay que decidir qué material se necesita, y antes de etiquetarlo hay que saber qué
significan las categorías. Los subpasos 1 a 5 son de investigación y decisión: no producen
datos. Los subpasos 6 a 8 son los primeros que generan archivos dentro de `data/raw/`.

| # | Subpaso | Estado |
| --- | --- | --- |
| 1 | Definir la estrategia del conjunto de datos | **Hecho** → [`03-estrategia-dataset.md`](03-estrategia-dataset.md) |
| 2 | Investigar conjuntos de datos públicos reales | Pendiente |
| 3 | Validar las categorías de clasificación | Pendiente |
| 4 | Decidir qué información puede obtenerse visualmente | Pendiente |
| 5 | Definir los criterios de etiquetado | Pendiente |
| 6 | Recolectar imágenes propias, si es necesario | Pendiente |
| 7 | Incorporar los conjuntos de datos públicos seleccionados | Pendiente |
| 8 | Organizar las imágenes originales | Pendiente |

**Todavía no existe un conjunto de datos definitivo**, ni se ha descargado ni capturado ninguna
imagen. El subpaso 3 recoge la validación de las categorías de tipo que quedó pendiente en
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md), sección 3b.

Se crea: `scripts/` (utilidades de captura y de organización de imágenes), **únicamente cuando
comience la captura o la organización de datos**, es decir en los subpasos 6 a 8. Mientras la
fase siga en investigación y documentación, la carpeta no se crea. También `data/raw/public/` y
`data/raw/own/`, cuando se incorpore material de cada origen.
Se agrega a `requirements.txt`: ya cubierto (OpenCV, NumPy).

### Fase 2 — Etiquetado y preparación de datos

Requiere que los subpasos 3 a 5 de la Fase 1 estén cerrados: no se puede etiquetar sin un
esquema de etiquetas ya validado. Con ese esquema definido, se anotan las imágenes por estado y
por tipo y se exportan las particiones de entrenamiento, validación y prueba, respetando la
regla de agrupación por huevo y por secuencia de video descrita en
[`03-estrategia-dataset.md`](03-estrategia-dataset.md), sección 8.

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

Se crea: `deploy/` y `docs/despliegue-aws.md`.

Los documentos que todavía no existen se nombran de forma descriptiva y sin número, para no
depender de una numeración rígida que puede chocar con los documentos que se creen antes.

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
| `data/raw/public/`, `data/raw/own/` | 1, al incorporar material de cada origen |
| `scripts/` | 1, solo al comenzar la captura u organización (subpasos 6 a 8) |
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
