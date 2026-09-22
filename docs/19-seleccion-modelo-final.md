# Selección del modelo final — YOLOv8n @ imgsz=960

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`18-experimento-yolov8n-960.md`](18-experimento-yolov8n-960.md) ·
[`17-evaluacion-baseline-yolov8n.md`](17-evaluacion-baseline-yolov8n.md) ·
[`16-entrenamiento-yolov8n.md`](16-entrenamiento-yolov8n.md)

---

## Decisión

**Modelo final actual del proyecto:** **YOLOv8n entrenado con `imgsz=960`**

Checkpoint en Drive:

`/content/drive/MyDrive/egg-detection/runs/yolov8n_960/weights/best.pt`

---

## Experimentos comparados

| | Baseline (exp. 1) | Experimento 2 (seleccionado) |
| --- | --- | --- |
| Modelo | YOLOv8n | YOLOv8n |
| imgsz | 640 | **960** |
| epochs | 50 | 50 |
| seed | 42 | 42 |
| Ultralytics | 8.4.158 | 8.4.158 |
| GPU | Tesla T4 | Tesla T4 |
| Run | `yolov8n_baseline` | `yolov8n_960` |

**Variable cambiada:** únicamente `imgsz`. No se evaluó YOLOv8s.

---

## Hipótesis del experimento 960

Del EDA: `crack` tiene área relativa mediana ~15× menor que `egg` y pierde detalle al
redimensionar a 640 px. Se planteó que **960 px** darían más resolución efectiva sobre
grietas finas sin cambiar arquitectura.

---

## Comparación de resultados

### Globales

| Split | Métrica | 640 | 960 | Mejor |
| --- | --- | ---: | ---: | --- |
| val | Recall | 0,816 | **0,872** | 960 |
| val | mAP50 | 0,862 | **0,895** | 960 |
| val | mAP50-95 | 0,682 | **0,720** | 960 |
| val | Precision | **0,900** | 0,878 | 640 |
| test | Precision | 0,888 | **0,909** | 960 |
| test | Recall | 0,820 | **0,830** | 960 |
| test | mAP50 | 0,844 | **0,885** | 960 |
| test | mAP50-95 | 0,673 | **0,707** | 960 |

### Crack — validation (foco de la hipótesis)

| Métrica | 640 (log) | 960 | Δ |
| --- | ---: | ---: | ---: |
| Recall | 0,640 | **0,744** | **+0,104** |
| mAP50 | 0,731 | **0,796** | **+0,065** |
| mAP50-95 | 0,369 | **0,445** | **+0,076** |
| Precision | **0,862** | 0,762 | −0,100 |

### Crack — test

Solo disponible para 960 (R=0,660, mAP50=0,776, mAP50-95=0,421). **No se afirma mejora
frente a 640** por falta de métricas por clase del test baseline.

---

## Coste computacional

| | Baseline 640 | Experimento 960 |
| --- | --- | --- |
| Tiempo entrenamiento | no documentado en JSON | **~79,6 min** |
| Tamaño checkpoint | ~6 MiB | ~6 MiB |
| Batch efectivo | no capturado | no capturado (`-1` en args.yaml) |
| Inferencia | más rápida (menor imgsz) | más lenta (mayor imgsz) |

El salto a 960 aumenta coste de entrenamiento e inferencia, pero el checkpoint mantiene
el mismo tamaño (nano). El trade-off se acepta por la mejora en detección de `crack` y
métricas globales de test.

---

## Motivos de la selección

1. **Recall de `crack` en val +10,4 pp** — menos falsos negativos en la clase objetivo.
2. **mAP50 y mAP50-95 de `crack` en val** mejoran de forma clara.
3. **Todas las métricas globales de test** mejoran frente a 640.
4. Misma arquitectura YOLOv8n — sin complejidad adicional de YOLOv8s.
5. `egg` permanece con rendimiento excelente.

---

## Limitaciones

1. **Precision de `crack` en val** baja con 960 (más falsos positivos posibles).
2. **crack-test vs baseline** no comparable por clase (dato no almacenado en exp. 1).
3. **Batch efectivo AutoBatch** no quedó registrado en `training_summary`.
4. **640 px val precision global** ligeramente superior — trade-off P vs R en val.
5. Modelo aún lejos de perfecto en `crack` (recall test 0,66).
6. Sin backend desplegado todavía — selección basada en métricas offline.
7. YOLOv8s **no evaluado** — posible experimento futuro si se necesita más capacidad.

---

## Próximos pasos (fuera de este documento)

- Copiar PNG de evaluación a `evaluation/yolov8n_960/`
- Integrar `best.pt` de `yolov8n_960` en pipeline de inferencia (FastAPI / móvil)
- No reentrenar salvo nuevo experimento explícito

---

## Referencias

- Baseline: [`evaluation/yolov8n_baseline/training_summary.json`](../evaluation/yolov8n_baseline/training_summary.json)
- Experimento 960: [`evaluation/yolov8n_960/training_summary.json`](../evaluation/yolov8n_960/training_summary.json)
