# Experimento 2 — YOLOv8n @ imgsz=960

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`17-evaluacion-baseline-yolov8n.md`](17-evaluacion-baseline-yolov8n.md) ·
[`16-entrenamiento-yolov8n.md`](16-entrenamiento-yolov8n.md) ·
[`14-eda-indigo.md`](14-eda-indigo.md)

> **Estado actual: PENDIENTE DE EJECUCIÓN EN GOOGLE COLAB**
>
> Notebook y documentación preparados. **No contiene resultados del experimento 960.**

---

## Hipótesis

Aumentar `imgsz` de **640 → 960** mejora la detección de grietas (`crack`) pequeñas,
manteniendo el mismo modelo **YOLOv8n** y el resto de variables controladas.

---

## Motivo del cambio (relación con EDA)

Del EDA INDIGO ([`14-eda-indigo.md`](14-eda-indigo.md)):

| Observación | Implicación |
| --- | --- |
| Resolución nativa ~3456×4608 | Reducir a 640 px comprime mucho el detalle |
| Área relativa mediana `crack` ≈ **0,015** vs `egg` ≈ **0,223** | `crack` ocupa muy pocos píxeles tras resize |
| 27 cajas `crack` con área relativa < 0,001 | Riesgo alto de perder grietas finas |
| Baseline: recall `crack` en log val ≈ **0,640** | Clase más difícil confirmada en práctica |

El experimento 960 busca dar más resolución efectiva a objetos pequeños **sin cambiar**
arquitectura ni dataset.

---

## Configuración prevista

| Parámetro | Baseline (exp. 1) | Experimento 2 |
| --- | --- | --- |
| Modelo | YOLOv8n | **YOLOv8n** (igual) |
| imgsz | 640 | **960** |
| epochs | 50 | 50 |
| seed | 42 | 42 |
| patience | 10 | 10 |
| batch | auto (`-1`) | auto (`-1`) |
| device | GPU 0 | GPU 0 |
| workers | 2 | 2 |
| train / val / test | 629 / 111 / 100 | **igual** |
| dataset | `indigo_yolo.zip` → `/content/indigo_yolo` | **igual** |

**Variable independiente:** `imgsz`  
**Variables controladas:** modelo, épocas, seed, patience, splits, pipeline, criterio de test único.

---

## Notebook y rutas

| Recurso | Ubicación |
| --- | --- |
| Notebook | [`notebooks/03_train_yolov8n_960_colab.ipynb`](../notebooks/03_train_yolov8n_960_colab.ipynb) |
| Baseline (no sobrescribir) | `/content/drive/MyDrive/egg-detection/runs/yolov8n_baseline/` |
| Run experimento 2 | `/content/drive/MyDrive/egg-detection/runs/yolov8n_960/` |

---

## Métricas a comparar

### Globales (val y test)

- Precision (`box.mp`)
- Recall (`box.mr`)
- mAP50 (`box.map50`)
- mAP50-95 (`box.map`)

### Por clase (prioridad `crack`)

- Precision, recall, mAP50, mAP50-95 de `egg` y `crack`
- Extraídas con `metrics.box.class_result(i)` / `summary()`

### Baseline de referencia (640 px, `training_summary.json`)

**Validation:**

| Métrica | Valor |
| --- | ---: |
| Precision | 0,9004 |
| Recall | 0,8160 |
| mAP50 | 0,8617 |
| mAP50-95 | 0,6817 |

**Test:**

| Métrica | Valor |
| --- | ---: |
| Precision | 0,8876 |
| Recall | 0,8204 |
| mAP50 | 0,8441 |
| mAP50-95 | 0,6725 |

**Log val por clase (baseline, referencia):** egg P≈0,995 R≈1,0; crack P≈0,862 **R≈0,640** mAP50≈0,731 mAP50-95≈0,369.

El notebook calcula **diferencias absolutas** (960 − 640) sin declarar automáticamente que 960 sea mejor.

---

## Criterios de análisis post-ejecución

1. **Recall de `crack`** — métrica clave de la hipótesis.
2. **mAP50 y mAP50-95 de `crack`** — localización de grietas finas.
3. **Coste computacional:**
   - batch real elegido por AutoBatch (VRAM)
   - tiempo de entrenamiento (wall clock)
   - velocidad de inferencia (`metrics.speed`)
   - tamaño de `best.pt` (debe ser similar; mismo YOLOv8n)

Si la mejora en `crack` es mínima pero el coste sube mucho, documentarlo explícitamente.

---

## Artefactos esperados en Drive

En `runs/yolov8n_960/`:

- `weights/best.pt`, `weights/last.pt`
- `results.png`, `results.csv`
- `confusion_matrix.png`, `confusion_matrix_normalized.png`
- `BoxPR_curve.png`, `BoxF1_curve.png`, `BoxP_curve.png`, `BoxR_curve.png`
- `training_summary.json`, `training_summary.csv` (incluye métricas por clase)

---

## Próximo paso

1. Ejecutar `notebooks/03_train_yolov8n_960_colab.ipynb` en Colab (GPU).
2. Actualizar este documento con resultados reales.
3. Crear `docs/19-evaluacion-yolov8n-960.md` y `evaluation/yolov8n_960/` tras la ejecución.

---

## Estado

**PENDIENTE DE EJECUCIÓN EN GOOGLE COLAB**
