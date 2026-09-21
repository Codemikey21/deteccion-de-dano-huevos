# Evaluación del baseline YOLOv8n — INDIGO

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`16-entrenamiento-yolov8n.md`](16-entrenamiento-yolov8n.md) ·
[`14-eda-indigo.md`](14-eda-indigo.md) · [`15-preparacion-yolo-indigo.md`](15-preparacion-yolo-indigo.md)

> Análisis del experimento baseline completado en Google Colab (Tesla T4, Ultralytics 8.4.158).
> **No se reentrenó.** **No se modificaron** `best.pt` ni `last.pt`.

---

## Resumen del experimento

| Campo | Valor |
| --- | --- |
| Modelo | YOLOv8n |
| Épocas | 50 |
| imgsz | 640 |
| seed | 42 |
| train / val / test | 629 / 111 / 100 |
| GPU | Tesla T4 |
| Ultralytics | 8.4.158 |

---

## Métricas en `training_summary.json`

Fuente: celda 14 del notebook, alimentada por la celda 9 (`model.val(split="val")`).

| Métrica | Valor JSON |
| --- | ---: |
| precision_val (`box.mp`) | 0,9004 |
| recall_val (`box.mr`) | 0,8160 |
| mAP50_val | 0,8617 |
| mAP50-95_val | 0,6817 |
| precision_test | 0,8876 |
| recall_test | 0,8204 |
| mAP50_test | 0,8441 |
| mAP50-95_test | 0,6725 |

---

## Log de validación de `best.pt` (Colab, verificado)

Tabla impresa por Ultralytics durante la validación de `best.pt` (split **val**):

| Clase | P | R | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| **all** | 0,928 | 0,820 | 0,863 | 0,682 |
| egg | 0,995 | 1,000 | 0,995 | 0,995 |
| crack | 0,862 | 0,640 | 0,731 | 0,369 |

Comprobación aritmética de la fila **all** (media macro por clase):

| Métrica | Cálculo | Resultado |
| --- | --- | ---: |
| P | (0,995 + 0,862) / 2 | **0,9285** |
| R | (1,000 + 0,640) / 2 | **0,8200** |
| mAP50 | (0,995 + 0,731) / 2 | **0,8630** |
| mAP50-95 | (0,995 + 0,369) / 2 | **0,6820** |

La fila **all** del log **sí es** el promedio macro de las filas por clase. **No** corresponde
a la métrica de una sola clase.

---

## Trazabilidad: log (P=0,928) vs JSON (precision_val=0,9004)

### Qué hace el notebook (verificado en código)

**Celda 9** — segunda validación explícita tras recargar `best.pt`:

```python
val_metrics = model.val(
    data=str(DATA_YAML),
    split="val",
    device=0,
    plots=True,
    save_json=True,
)

def extract_box_metrics(metrics):
    box = metrics.box
    return {
        "precision": float(box.mp),
        "recall": float(box.mr),
        "mAP50": float(box.map50),
        "mAP50_95": float(box.map),
    }

val_scores = extract_box_metrics(val_metrics)
```

**Celda 14** — persiste `val_scores["precision"]` como `precision_val`.

### API Ultralytics implicada

| Campo JSON | Propiedad leída | Definición en Ultralytics 8.4.x |
| --- | --- | --- |
| precision_val | `metrics.box.mp` | `mean(box.p)` — media macro de P por clase |
| recall_val | `metrics.box.mr` | `mean(box.r)` — media macro de R por clase |
| mAP50_val | `metrics.box.map50` | mAP@0.5 medio |
| mAP50-95_val | `metrics.box.map` | mAP@0.5:0.95 medio |

La fila **all** que imprime Ultralytics en consola usa `metrics.mean_results()`, que devuelve
**exactamente** `[mp, mr, map50, map]` — la misma API que lee `extract_box_metrics`.

Por tanto, **en una misma ejecución de `model.val()`**, el valor impreso en **all → P** y
`precision_val` guardado **deberían coincidir**. No es posible que 0,928 y 0,9004 provengan
del mismo objeto retornado en la misma llamada sin un bug de Ultralytics (no observado aquí).

### Validaciones distintas en el flujo del notebook

El notebook ejecuta **al menos dos** validaciones sobre `best.pt`:

| # | Momento | Código | ¿Alimenta `training_summary.json`? |
| --- | --- | --- | --- |
| 1 | Fin de `model.train()` (celda 7) | `final_eval()` → `validator(model=best.pt)` | **No** |
| 2 | Celda 9 | `model.val(split="val", plots=True, save_json=True)` | **Sí** → `val_scores` |

No hay evidencia en el repositorio de que el log P=0,928 pertenezca a la ejecución 1 o 2.
Tampoco hay captura de la salida impresa de la celda 9 (`=== Métricas VALIDATION ===`).

### Parámetros que difieren entre ejecuciones

| Aspecto | `final_eval` (fin de train) | Celda 9 `model.val()` |
| --- | --- | --- |
| Instancia validator | Reutiliza validator del Trainer | Crea validator nuevo |
| `plots` | Hereda de args de entrenamiento | `True` explícito |
| `save_json` | No forzado en notebook | `True` explícito |
| Modelo | Path `best.pt` | `YOLO(best.pt)` recargado |
| `split` | Default val | `split="val"` explícito |

No se encontró en el notebook: sobrescritura de `val_scores`, uso de `train_results`, ni
lectura de métricas de test mezcladas en `precision_val`.

### Estado de la discrepancia

| Observación | Detalle |
| --- | --- |
| Log all P | **0,928** (coherente con egg/crack) |
| JSON precision_val | **0,9004** |
| Δ P | **−0,0276** |
| Log all R vs JSON | 0,820 vs 0,8160 (Δ −0,004) |
| Log mAP50 vs JSON | 0,863 vs 0,8617 (Δ −0,0013) |
| Log mAP50-95 vs JSON | 0,682 vs 0,6817 (Δ −0,0003) |

mAP casi coincide; **precision macro diverge más** que recall y mAP.

**Conclusión verificable:** el JSON refleja el retorno de la celda 9 vía `box.mp`. El log
P=0,928 es coherente con las métricas por clase documentadas arriba. **No se puede demostrar
desde el repositorio local** si el log proviene de la validación 1, de la 2, o de una
re-ejecución parcial de celdas en Colab.

**Estado: pendiente de trazabilidad.** Para cerrarlo haría falta conservar la salida completa
de la celda 9 y/o ejecutar una sola vez:

```python
results = model.val(data=str(DATA_YAML), split="val", verbose=True)
print("printed mp should match:", results.box.mp)
print(results.summary())
```

---

## Comparación validation vs test (desde JSON)

| Métrica | val (JSON) | test | Δ |
| --- | ---: | ---: | ---: |
| Precision | 0,9004 | 0,8876 | −0,0128 |
| Recall | 0,8160 | 0,8204 | +0,0044 |
| mAP50 | 0,8617 | 0,8441 | −0,0176 |
| mAP50-95 | 0,6817 | 0,6725 | −0,0092 |

Test queda ligeramente por debajo en mAP; variación acotada.

---

## Comportamiento por clase (log Colab verificado)

| Clase | P | R | mAP50 | mAP50-95 | Lectura |
| --- | ---: | ---: | ---: | ---: | --- |
| egg | 0,995 | 1,000 | 0,995 | 0,995 | Detección casi perfecta en val |
| crack | 0,862 | 0,640 | 0,731 | 0,369 | Clase más difícil; recall bajo |

**crack** concentra el error: recall 0,640 y mAP50-95 0,369 frente a egg ~0,995. Coherente
con el EDA (grietas mucho más pequeñas que el huevo a `imgsz=640`).

---

## Fortalezas

1. Pipeline Colab reproducible (ZIP → `/content` → train → val → test).
2. mAP50 val en log **≈ 0,86**; test JSON **≈ 0,84**.
3. `egg` muy bien detectado en val.
4. Checkpoints en Drive.

---

## Limitaciones

1. `imgsz=640` sobre imágenes ~3456×4608.
2. **crack**: recall 0,640 en log de val — falsos negativos significativos.
3. Discrepancia P entre log (0,928) y JSON (0,9004) **sin trazabilidad cerrada**.
4. PNG de entrenamiento aún no copiados a `evaluation/yolov8n_baseline/`.

---

## Siguiente experimento propuesto (NO ejecutado)

| Parámetro | Baseline | Propuesta |
| --- | --- | --- |
| Modelo | YOLOv8n | YOLOv8n |
| imgsz | 640 | **960** |
| epochs / seed / batch / patience | 50 / 42 / auto / 10 | iguales |
| dataset / splits | iguales | iguales |

Objetivo: más píxeles efectivos sobre grietas pequeñas, sin YOLOv8s todavía.

---

## Artefactos en Git

| Archivo | Estado |
| --- | --- |
| `evaluation/yolov8n_baseline/training_summary.json` | ✅ |
| `evaluation/yolov8n_baseline/training_summary.csv` | ✅ |
| `evaluation/yolov8n_baseline/README.md` | ✅ |
| PNG (`results.png`, matrices, curvas) | ⏳ Descargar manualmente desde Drive |

No incluidos: `best.pt`, `last.pt`, `indigo_yolo.zip`.
