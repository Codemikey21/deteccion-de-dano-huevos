# Experimento 2 — YOLOv8n @ imgsz=960

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`19-seleccion-modelo-final.md`](19-seleccion-modelo-final.md) ·
[`17-evaluacion-baseline-yolov8n.md`](17-evaluacion-baseline-yolov8n.md) ·
[`14-eda-indigo.md`](14-eda-indigo.md)

> **Estado actual: EXPERIMENTO COMPLETADO**
>
> Ejecutado en Google Colab (Tesla T4, Ultralytics 8.4.158).

---

## Hipótesis

Aumentar `imgsz` de **640 → 960** mejora la detección de grietas (`crack`) pequeñas,
manteniendo **YOLOv8n** y el resto de variables controladas.

---

## Configuración ejecutada

| Parámetro | Baseline (640) | Experimento 2 (960) |
| --- | --- | --- |
| Modelo | YOLOv8n | YOLOv8n |
| imgsz | 640 | **960** |
| epochs | 50 | 50 |
| seed | 42 | 42 |
| patience | 10 | 10 |
| batch | auto (`-1`) | auto (`-1`) |
| train / val / test | 629 / 111 / 100 | 629 / 111 / 100 |

Run: `/content/drive/MyDrive/egg-detection/runs/yolov8n_960/`

---

## Resultados reales — globales

### Validation

| Métrica | 640 | 960 | Δ (960−640) |
| --- | ---: | ---: | ---: |
| Precision | 0,9004 | 0,8782 | −0,0222 |
| Recall | 0,8160 | 0,8722 | **+0,0562** |
| mAP50 | 0,8617 | 0,8955 | **+0,0338** |
| mAP50-95 | 0,6817 | 0,7201 | **+0,0385** |

### Test

| Métrica | 640 | 960 | Δ (960−640) |
| --- | ---: | ---: | ---: |
| Precision | 0,8876 | 0,9094 | **+0,0218** |
| Recall | 0,8204 | 0,8302 | **+0,0098** |
| mAP50 | 0,8441 | 0,8845 | **+0,0403** |
| mAP50-95 | 0,6725 | 0,7073 | **+0,0348** |

---

## Resultados reales — por clase

### Validation

| Clase | Métrica | 640 (ref.) | 960 | Δ |
| --- | --- | ---: | ---: | ---: |
| egg | P / R / mAP50 / mAP50-95 | ~0,995 / 1,0 / 0,995 / 0,995 | 0,994 / 1,0 / 0,995 / 0,995 | ≈0 |
| crack | Precision | ~0,862 | 0,762 | −0,100 |
| crack | **Recall** | **0,640** | **0,744** | **+0,104** |
| crack | **mAP50** | **0,731** | **0,796** | **+0,065** |
| crack | **mAP50-95** | **0,369** | **0,445** | **+0,076** |

Referencia 640 crack-val: log verificado de `best.pt` baseline.

### Test (solo 960 — sin baseline por clase)

| Clase | P | R | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| egg | 0,984 | 1,000 | 0,993 | 0,993 |
| crack | 0,835 | 0,660 | 0,776 | 0,421 |

**No se compara crack-test 960 vs 640** porque no hay métricas por clase de test del baseline.

---

## Coste computacional

| Concepto | Valor |
| --- | --- |
| Tiempo entrenamiento | **4777 s (~79,6 min)** |
| Tamaño `best.pt` | **~5,99 MiB** (igual arquitectura YOLOv8n) |
| Batch solicitado | auto (`-1`) |
| Batch efectivo | **No capturado** (`args.yaml` conservó `-1`; ver log AutoBatch en Colab) |

Mayor `imgsz` implica más VRAM y tiempo por época; el tamaño del checkpoint no cambia (mismo YOLOv8n).

---

## Conclusión del experimento

1. **Hipótesis principal (crack en val):** recall (+10,4 pp), mAP50 (+6,5 pp) y mAP50-95 (+7,6 pp)
   mejoran frente al baseline 640. Precision de crack en val baja (~−10 pp).
2. **Métricas globales test:** todas mejoran frente a 640.
3. **egg** sigue casi perfecto en val y test.

**YOLOv8n @ imgsz=960 queda seleccionado como modelo final actual** — ver
[`19-seleccion-modelo-final.md`](19-seleccion-modelo-final.md).

---

## Artefactos

| Ubicación | Contenido |
| --- | --- |
| Drive `runs/yolov8n_960/` | `best.pt`, curvas, matrices, JSON/CSV originales |
| Git `evaluation/yolov8n_960/` | Copia ligera JSON/CSV (+ PNG pendientes de copiar) |

---

## Estado

**EXPERIMENTO COMPLETADO**
