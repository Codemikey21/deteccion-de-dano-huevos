# Preparación del dataset INDIGO para YOLOv8

Asignatura: Ciencia de Datos — Ingeniería de Sistemas  
Fecha: 21 de septiembre de 2026  
Documentos relacionados: [`14-eda-indigo.md`](14-eda-indigo.md) ·
[`13-validacion-final-indigo.md`](13-validacion-final-indigo.md) ·
[`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)

> **No se entrenó ningún modelo.** No se abrió Colab. No se redimensionaron imágenes.
> No se aplicó augmentation. `data/raw/indigo/` **no fue modificado**.

Script reproducible: `python scripts/convert_voc_to_yolo.py --force`  
Resumen JSON: `evaluation/yolo_conversion/conversion_summary.json`  
Visualizaciones: `evaluation/yolo_conversion/`

---

## Objetivo

Generar una versión procesada compatible con Ultralytics YOLOv8 en
`data/processed/indigo_yolo/`, copiando las imágenes necesarias desde el dataset raw
(sin symlinks) y convirtiendo las anotaciones Pascal VOC a formato YOLO normalizado.

---

## Conversión VOC → YOLO

Para cada XML Pascal VOC se extrajeron las cajas `bndbox` y se convirtieron a:

```text
<class_id> <x_center> <y_center> <width> <height>
```

con coordenadas normalizadas entre 0 y 1 respecto al tamaño de la imagen:

| Campo YOLO | Fórmula |
| --- | --- |
| `x_center` | `(xmin + xmax) / 2 / img_width` |
| `y_center` | `(ymin + ymax) / 2 / img_height` |
| `width` | `(xmax - xmin) / img_width` |
| `height` | `(ymax - ymin) / img_height` |

### Mapeo de clases (exacto)

| Clase VOC | ID YOLO |
| --- | --- |
| `egg` | **0** |
| `crack` | **1** |

Si aparece cualquier otra clase, el script **detiene el proceso** y muestra error.
Durante esta ejecución no se encontró ninguna clase distinta de `egg` o `crack`.

---

## División train / val / test

| Origen | Destino | Imágenes |
| --- | --- | --- |
| `test/test_100/` (original) | **test** | **100** (intacto) |
| `train/train_100/` (740 orig.) | **train** (~85 %) | **629** |
| `train/train_100/` (740 orig.) | **val** (~15 %) | **111** |

- **Seed fijo:** `42`
- **Ratio train/val:** `0.85` sobre las 740 imágenes originales de train
- Las 100 imágenes originales de test **no se mezclaron** con train ni val

No se aplicó estratificación por clases: casi todas las imágenes contienen `egg` y `crack`
(815/840 en el EDA), por lo que un split aleatorio simple es representativo.

---

## Estructura generada

```text
data/processed/indigo_yolo/
├── images/
│   ├── train/    (629 JPEG)
│   ├── val/      (111 JPEG)
│   └── test/     (100 JPEG)
├── labels/
│   ├── train/    (629 TXT)
│   ├── val/      (111 TXT)
│   └── test/     (100 TXT)
└── data.yaml
```

### `data.yaml`

```yaml
path: <ruta_absoluta_a_indigo_yolo>
train: images/train
val: images/val
test: images/test
nc: 2
names:
  0: egg
  1: crack
```

En Colab, actualizar la línea `path` a la ubicación donde se copie la carpeta
(p. ej. `/content/indigo_yolo`). Las rutas `train`, `val` y `test` son relativas a `path`.

---

## Cantidades finales

| Split | Imágenes | Labels | Instancias `egg` | Instancias `crack` |
| --- | --- | --- | --- | --- |
| train | 629 | 629 | 628 | 713 |
| val | 111 | 111 | 111 | 125 |
| test | 100 | 100 | 99 | 107 |
| **Total** | **840** | **840** | **838** | **945** |

Los totales de instancias coinciden con el EDA previo (1783 objetos).

---

## Distribución de clases por split

| Split | Contiene `egg` | Contiene `crack` |
| --- | --- | --- |
| train | Sí | Sí |
| val | Sí | Sí |
| test | Sí | Sí |

Proporción aproximada egg:crack por split:

- train: 46,9 % egg / 53,1 % crack
- val: 47,0 % egg / 53,0 % crack
- test: 48,0 % egg / 52,0 % crack

La distribución es coherente entre splits; no se afirma estratificación perfecta porque
no fue necesaria ni aplicada.

---

## Espacio en disco

| Concepto | Valor |
| --- | --- |
| Estimación previa a la copia | **2,243 GiB** (2 408 861 345 bytes) |
| Espacio real copiado (solo JPEG) | **2,243 GiB** (2 408 861 345 bytes) |
| Tamaño total de `indigo_yolo/` (imgs + labels + yaml) | **~2,24 GiB** |

Estrategia: **copia física** de JPEG (no symlinks) para portabilidad a Google Colab.

---

## Validaciones realizadas

| Comprobación | Resultado |
| --- | --- |
| Imágenes train / val / test | 629 / 111 / 100 |
| Labels train / val / test | 629 / 111 / 100 |
| Imágenes sin label | **0** |
| Labels sin imagen | **0** |
| Coordenadas fuera de [0, 1] | **0** |
| `width <= 0` o `height <= 0` | **0** |
| Clases distintas de 0 o 1 | **0** |
| `data/raw/indigo/` intacto (conteos + bytes + mtime) | **Sí** |

---

## Comparación XML vs YOLO

Se seleccionaron **8 imágenes al azar** (seed 42) repartidas entre train, val y test.
Para cada una:

1. Se leyeron las cajas del XML Pascal VOC original.
2. Se leyeron las cajas del TXT YOLO convertido.
3. Se transformaron las coordenadas YOLO de vuelta a píxeles.
4. Se compararon con tolerancia de **2 px**.

| Imagen (muestra) | Objetos | Diferencia máx. (px) | OK |
| --- | --- | --- | --- |
| val/IMG_20220816_144745.jpg | 2 | 0,0 | Sí |
| train/IMG_20220817_151659.jpg | 2 | 0,0 | Sí |
| train/IMG_20220812_105737.jpg | 2 | 0,0 | Sí |
| test/IMG_20220818_154335.jpg | 2 | 0,0 | Sí |
| train/IMG_20220816_142058.jpg | 2 | 0,0 | Sí |
| train/IMG_20220816_141101.jpg | 2 | 0,0 | Sí |
| train/IMG_20220816_140953.jpg | 3 | 0,0 | Sí |
| train/IMG_20220816_142908.jpg | 2 | 0,0 | Sí |

**8/8 conversiones coinciden exactamente** (diferencia 0 px).

---

## Validación visual

Se generaron **6 imágenes** con las cajas YOLO dibujadas sobre la copia procesada:

- `evaluation/yolo_conversion/train_IMG_20220812_104709_yolo.png`
- `evaluation/yolo_conversion/train_IMG_20220812_105815_yolo.png`
- `evaluation/yolo_conversion/train_IMG_20220816_145343_yolo.png`
- `evaluation/yolo_conversion/train_IMG_20220817_152936_yolo.png`
- `evaluation/yolo_conversion/val_IMG_20220816_150453_yolo.png`
- `evaluation/yolo_conversion/test_IMG_20220818_154847_yolo.png`

Verde = `egg` (0), rojo = `crack` (1). Las imágenes originales en `data/raw/indigo/` no
fueron modificadas.

---

## Problemas encontrados

**Ninguno.** La conversión completó sin errores, sin clases desconocidas, sin pares
huérfanos y sin coordenadas inválidas.

---

## Resultado final

### LISTO PARA ENTRENAMIENTO YOLOV8

El dataset procesado cumple la estructura, el mapeo de clases, los splits y todas las
validaciones automáticas. El siguiente paso (fuera de este documento) será entrenar
YOLOv8n en Google Colab GPU usando `data/processed/indigo_yolo/data.yaml`.
