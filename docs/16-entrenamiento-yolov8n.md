# Entrenamiento baseline YOLOv8n — INDIGO

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`15-preparacion-yolo-indigo.md`](15-preparacion-yolo-indigo.md) ·
[`17-evaluacion-baseline-yolov8n.md`](17-evaluacion-baseline-yolov8n.md) ·
[`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)

> **Estado actual: ENTRENAMIENTO BASELINE COMPLETADO**
>
> Ejecutado en Google Colab GPU (Tesla T4). Métricas reales documentadas abajo.

---

## Objetivo del baseline

Entrenar un detector **YOLOv8n** (nano) sobre el dataset INDIGO convertido a YOLO como
**línea base** del proyecto.

---

## Entorno de ejecución

| Parámetro | Valor |
| --- | --- |
| GPU | **Tesla T4** |
| Ultralytics | **8.4.158** |
| Notebook | [`notebooks/02_train_yolov8_indigo_colab.ipynb`](../notebooks/02_train_yolov8_indigo_colab.ipynb) |
| Dataset (local Colab) | `/content/indigo_yolo/` |
| Dataset (ZIP Drive) | `/content/drive/MyDrive/egg-detection/datasets/indigo_yolo.zip` |
| Runs (Drive) | `/content/drive/MyDrive/egg-detection/runs/yolov8n_baseline/` |

---

## Configuración del entrenamiento

| Parámetro | Valor |
| --- | --- |
| Modelo | `YOLO("yolov8n.pt")` |
| Épocas | **50** |
| `imgsz` | **640** |
| Batch | auto (`batch=-1`) |
| Patience | 10 |
| Seed | **42** |
| Workers | 2 |

---

## Dataset

| Split | Imágenes | Uso |
| --- | ---: | --- |
| train | **629** | Entrenamiento |
| val | **111** | Validación y early stopping |
| test | **100** | Evaluación final única |

Clases: `0 = egg`, `1 = crack`

---

## Métricas reales — Validation (`val`)

Evaluación con `model.val(split="val")` sobre `best.pt`.  
API usada en `training_summary.json`: `metrics.box.mp`, `metrics.box.mr`, `metrics.box.map50`, `metrics.box.map`.

| Métrica | Valor |
| --- | ---: |
| Precision (mp) | **0,9004** |
| Recall (mr) | **0,8160** |
| mAP50 | **0,8617** |
| mAP50-95 | **0,6817** |

---

## Métricas reales — Test final (`test`)

Evaluación **única** con `model.val(split="test")` sobre `best.pt`.

| Métrica | Valor |
| --- | ---: |
| Precision (mp) | **0,8876** |
| Recall (mr) | **0,8204** |
| mAP50 | **0,8441** |
| mAP50-95 | **0,6725** |

---

## Diferencia validation vs test

| Métrica | val | test | Δ (test − val) |
| --- | ---: | ---: | ---: |
| Precision | 0,9004 | 0,8876 | −0,0128 |
| Recall | 0,8160 | 0,8204 | +0,0044 |
| mAP50 | 0,8617 | 0,8441 | −0,0176 |
| mAP50-95 | 0,6817 | 0,6725 | −0,0092 |

El test queda ligeramente por debajo de val en mAP, con variación acotada. No hay evidencia
de sobreajuste severo entre splits.

---

## Nota sobre precision en logs vs `training_summary.json`

El log de validación de `best.pt` en Colab mostró **all → P ≈ 0,928** (media macro de
egg=0,995 y crack=0,862), mientras `training_summary.json` registra **precision_val = 0,9004**
desde `metrics.box.mp` en la celda 9 del notebook.

Ambos usan la misma API (`box.mp` = fila **all**), por lo que **no deberían divergir en una
misma ejecución de `model.val()`**. La causa exacta queda **pendiente de trazabilidad**
(posibles validaciones distintas: fin de `model.train()` vs celda 9).

Análisis completo en [`17-evaluacion-baseline-yolov8n.md`](17-evaluacion-baseline-yolov8n.md).

---

## Checkpoints y artefactos

| Artefacto | Ubicación (Google Drive) |
| --- | --- |
| `best.pt` | `.../runs/yolov8n_baseline/weights/best.pt` |
| `last.pt` | `.../runs/yolov8n_baseline/weights/last.pt` |
| `training_summary.json` | `.../runs/yolov8n_baseline/training_summary.json` |
| Curvas y matrices | `.../runs/yolov8n_baseline/*.png` |

Copia ligera en Git: `evaluation/yolov8n_baseline/` (JSON/CSV; PNG pendientes de descarga manual).

**No versionar** `best.pt` ni `last.pt` en Git.

---

## Conclusión del baseline

- Pipeline Colab completo: extracción ZIP → entrenamiento → val → test → exportación.
- Detector funcional con **mAP50 val ≈ 0,86** y **mAP50 test ≈ 0,84**.
- Generalización razonable entre val y test.
- Checkpoints persistidos en Drive.
- Siguiente paso propuesto (no ejecutado): YOLOv8n con `imgsz=960` — ver doc 17.

---

## Estado

**ENTRENAMIENTO BASELINE COMPLETADO**
