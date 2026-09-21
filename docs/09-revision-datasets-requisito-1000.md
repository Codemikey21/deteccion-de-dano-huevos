# Revisión de conjuntos de datos: requisito de 1.000 imágenes reales

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase 1, revisión: el conjunto de entrenamiento debe tener como mínimo 1.000 imágenes reales
Documentos relacionados: [`03-estrategia-dataset.md`](03-estrategia-dataset.md) ·
[`04-investigacion-datasets.md`](04-investigacion-datasets.md) ·
[`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md) ·
[`07-validacion-fuentes-dataset.md`](07-validacion-fuentes-dataset.md)

> **No se ha descargado ningún conjunto nuevo.** Esta investigación consulta metadatos y fichas
> públicas. `scripts/download_detection_dataset.py` y `data/raw/detection/` **se conservan**.

---

## 1. Nuevo requisito académico

El profesor exige que el conjunto utilizado para el **entrenamiento** tenga como mínimo:

**1.000 imágenes reales.**

Reglas de interpretación que se adoptan a partir de ahora:

| Qué cuenta | Qué no cuenta |
| --- | --- |
| Fotografías reales distintas | 1.000 cajas en pocas imágenes |
| Imágenes originales de un conjunto público | Imágenes generadas solo por *data augmentation* |
| Capturas propias reales | Duplicados, fotogramas casi idénticos de la misma secuencia |

El *augmentation* **sí** podrá usarse más adelante para mejorar el entrenamiento. **No** podrá
usarse para presentar 1.000 imágenes originales cuando no las hay.

Objetivo operativo, si los datos lo permiten: **1.200 a 2.000 imágenes reales** en el conjunto
final (público + propio), para no quedar pegados al mínimo.

El requisito aplica a **las dos tareas del MVP**, por separado:

- **A. Detección** de `egg`: el conjunto con el que se entrena el detector debe tener ≥ 1.000
  imágenes reales.
- **B. Clasificación de estado** (`bueno`, `grieta`, `sucio`, `danado`): el conjunto con el que
  se entrena el clasificador también debe tener ≥ 1.000 imágenes reales.

No se exige que un solo archivo público cubra las dos tareas.

---

## 2. Impacto sobre la estrategia anterior

Inicialmente se seleccionó **Egg-Detection** (`afshin-dini/Egg-Detection`) como candidato
principal de detección, por licencia MIT verificada y formato YOLO. Esa decisión queda
documentada en [`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md) y **no se borra**.

Al conocerse el requisito de 1.000 imágenes reales, esa selección **deja de ser suficiente como
fuente principal**. El conjunto se **conserva** y se reclasifica como
**DATASET COMPLEMENTARIO DE DETECCIÓN**.

La estrategia pasa a ser:

```
datasets públicos verificados
+ capturas propias
= conjunto final ≥ 1.000 imágenes reales
  (objetivo 1.200–2.000 si es viable)
```

No se asume que el equipo deba fotografiar las 1.000 por sí solo si existen fuentes públicas
apropiadas.

---

## 3. Qué se conserva de Egg-Detection

| Campo | Valor auditado (sin descarga de imágenes) |
| --- | --- |
| Identificador | `afshin-dini/Egg-Detection` |
| URL | https://huggingface.co/datasets/afshin-dini/Egg-Detection |
| Imágenes reales | **51** (49 `train`, 2 `val`) |
| Bounding boxes | **423** |
| Archivos | 108 |
| Tamaño | 339,47 MiB ≈ 355,96 MB |
| Formato | YOLO |
| Licencia | **MIT** (API de Hugging Face, 21/09/2026) |
| Clases | **PENDIENTE DE VERIFICACIÓN** (`data.yaml` no leído) |
| Script | `scripts/download_detection_dataset.py` **se conserva** |
| Documentación | `data/raw/detection/README.md` **se conserva** |

Sigue siendo útil para:

- aportar ejemplos adicionales de detección;
- aportar escenas con **varios huevos por imagen** (~8 cajas/imagen);
- complementar un conjunto principal más grande;
- comparar dominio visual entre fuentes (bandeja/cartón vs. banda).

**No se descarta. No se borra. No se deja de descargar cuando toque.** Simplemente **no cumple
el mínimo de 1.000 imágenes**.

---

## 4. Qué ya no es suficiente

| Fuente | Imágenes reales | ¿Cubre 1.000 sola? |
| --- | --- | --- |
| Egg-Detection | 51 | **No** |
| INDIGO (grietas, figshare) | 840 | **No** |
| Egg-Detection + INDIGO | 891 | **No** (faltan ≥ 109) |
| Good and Bad Eggs, solo originales | 1.000 | **Sí en volumen**, no en taxonomía de estado |
| Good and Bad Eggs + 6.000 aumentadas | 1.000 reales | Las 6.000 **no cuentan** para el requisito |

Ninguna de las fuentes **ya aprobadas por licencia** cubre a la vez detección, las cuatro clases
de estado y el mínimo de 1.000. Hay que ampliar el inventario.

---

## 5. Dos necesidades distintas

### A. Detección de `egg`

Hacen falta ≥ 1.000 imágenes reales con huevos localizables (idealmente con cajas). Egg-Detection
puede entrar en el conjunto final. Se necesita una fuente **mucho más grande** o una combinación
que sume el mínimo.

### B. Clasificación del estado

Hacen falta ≥ 1.000 imágenes reales etiquetables como `bueno`, `grieta`, `sucio`, `danado`.

Distribución **orientativa**, no obligatoria:

| Clase | Rango deseable |
| --- | --- |
| `bueno` | 300–500 |
| `grieta` | 300–500 |
| `sucio` | 300–500 |
| `danado` | 300–500 |

Si los datos reales no lo permiten, se documentará el desbalance; no se inventarán imágenes.

La captura propia de las **cuatro clases** sigue siendo **obligatoria** (mismo escenario, para
que el modelo no aprenda la fuente). No es obligatorio que esas capturas sean las 1.000.

---

## 6. Nuevos conjuntos candidatos

Además de reevaluar los ya documentados en `docs/04` y `docs/07`, se buscaron fuentes en Hugging
Face, Roboflow Universe, Kaggle, Mendeley Data, Figshare, Zenodo, Ultralytics Platform y
literatura. Fecha de consulta: **21/09/2026**.

### 6.1 Conjuntos con licencia verificada (reales, ≥ 1.000 o cercanos)

#### Egg Variety Recognition — Mendeley Data (nueva verificación de licencia)

| Campo | Valor |
| --- | --- |
| Nombre | A Machine-Vision Framework for Automated Egg Variety Recognition… |
| URL | https://data.mendeley.com/datasets/49msr3ksxj/2 |
| DOI | 10.17632/49msr3ksxj.2 |
| Imágenes reales | **9.100 originales** + 2.250 con moneda. La fuente declara que **no se aplicó aumentación** al conjunto de clasificación |
| Anotaciones | Clasificación por especie y frescura. **No se declaran bounding boxes** |
| Clases | Bird Koel, Country Chicken, Red Layer, White Layer, Duck; más frescura día 0 / 25 / 45 |
| Licencia | **CC BY 4.0** — DataCite, `rightsIdentifier` = `cc-by-4.0`, consultada el 21/09/2026 |
| Tamaño | No especificado por la fuente consultada |
| Detección | **Volumen sí, cajas no.** Habría que anotar huevos o usarlo solo si cada foto es un huevo recortado (no verificado) |
| Estado | **No.** Eje de especie/frescura, no `bueno/grieta/sucio/danado` |

Es el mayor conjunto de **imágenes reales de huevo** con licencia permisiva confirmada. No
resuelve el estado. Puede ayudar al detector **solo si** se confirma que cada imagen es un huevo
aprovechable o si se añaden cajas.

#### Good and Bad Eggs — Mendeley Data (ya documentado)

| Campo | Valor |
| --- | --- |
| URL / DOI | https://data.mendeley.com/datasets/mdty358x8m/1 · 10.17632/mdty358x8m.1 |
| Imágenes reales | **1.000 originales** |
| Aumentadas | 6.000 — **no cuentan** para el requisito |
| Anotaciones | Clasificación binaria |
| Clases | good / bad |
| Licencia | **CC BY 4.0** |
| Tamaño | No especificado por la fuente consultada |
| Detección | No (sin cajas declaradas) |
| Estado | Candidato a volumen de `bueno` **si** la etiqueta sobrevive a inspección. `bad` no es remapable a una sola de nuestras clases |

Cumple el mínimo **en cantidad**. No cumple la taxonomía de cuatro estados.

#### INDIGO crack detection — figshare (ya documentado)

| Campo | Valor |
| --- | --- |
| DOI | 10.6084/m9.figshare.21568425.v1 |
| Imágenes reales | **840** (740 train, 100 test) |
| Anotaciones | Cajas, clases `egg` y `crack` |
| Licencia | **CC BY 4.0** |
| Tamaño | ≈ 2,5 GB |
| Detección | Útil; **no llega a 1.000** |
| Estado | Cubre `grieta` (frontera con `danado` no validada) |

#### Egg-Detection — Hugging Face (complementario, se conserva)

Ver sección 3. **51 imágenes.** MIT. YOLO.

### 6.2 Candidatos grandes cuya licencia o recuento sigue pendiente

#### egg_dataset — Ultralytics Platform (nuevo)

| Campo | Valor |
| --- | --- |
| Nombre | egg_dataset (autor: Ahmed Raza) |
| URL | https://platform.ultralytics.com/ahmed-raza/datasets/eggdataset |
| Imágenes | **2.553** (2.530 etiquetadas; split 2.316 / 227 / 10) |
| Anotaciones | 5.517; detección de objetos |
| Clases | 2: **normal** y **cracked** (declaradas en la ficha) |
| Escenario | Cinta industrial de clasificación de huevos |
| Tamaño | 125,6 MB |
| Licencia | **PENDIENTE DE VERIFICACIÓN** (la ficha consultada no la muestra) |
| Detección | **Alta, si la licencia es usable:** supera 1.000 y el escenario se parece al nuestro |
| Estado | `normal`/`cracked` → candidatos a `bueno`/`grieta`, **sin validar**. No cubre `sucio` ni `danado` |

Es el candidato **más prometedor en volumen + escenario** encontrado en esta revisión. **No se
elige todavía** porque falta la licencia.

#### yolov11-eggs — Roboflow Universe (nuevo)

| Campo | Valor |
| --- | --- |
| URL | https://universe.roboflow.com/moe-gtdgx/yolov11-eggs |
| Imágenes | **2,1k** (fragmento indexado; ficha bloqueada por Cloudflare) |
| Clases | Extra Large, jumbo, large, medium, small |
| Licencia | CC BY 4.0 **según el fragmento indexado** → **PENDIENTE DE VERIFICACIÓN** |
| Detección | Posible: son huevos con cajas, aunque las clases son de **calibre**, no de `egg` único |
| Estado | **No** |

#### egg (ali salah) — Roboflow Universe (nuevo)

| Campo | Valor |
| --- | --- |
| URL | https://universe.roboflow.com/ali-salah/egg-m8acg |
| Imágenes | **~1k** (“See all 1k images”; ficha bloqueada) |
| Clases | `Cracked Egg Brown`, `Cracked Egg White`, `Normal Egg White`, y `af-1KPR` (significado no verificado) |
| Licencia | **PENDIENTE DE VERIFICACIÓN** |
| Detección / estado | Posible para `egg` + `grieta`/`bueno`. `af-1KPR` es opaco |

#### Egg Quality Grading — Roboflow (ya documentado)

~1.100 imágenes; clases mezcladas (color + suciedad + calcio + sangre). Licencia
**PENDIENTE DE VERIFICACIÓN**. Útil solo el subconjunto de suciedad, si existe y se extrae.

#### Detection Of cracked eggs — Roboflow (ya documentado)

~1.200 imágenes; solo huevos agrietados. Licencia **PENDIENTE DE VERIFICACIÓN**.

#### egg detection — 360DIGITMG / Roboflow (nuevo; cifras contradictorias)

| Campo | Valor |
| --- | --- |
| URL | https://universe.roboflow.com/360digitmg-f1mel/egg-detection-tdz3d |
| Imágenes | El **espacio** del autor muestra **2,56k**; un **modelo** del mismo proyecto declara **91**. **No se puede tomar ninguna de las dos como cifra confirmada** |
| Clases (fragmento) | `blurr white egg`, `blurr-brown-eggs`, `brown eggs` |
| Licencia | **PENDIENTE DE VERIFICACIÓN** |

#### MMU Egg Grading — Kaggle (ya documentado)

3.641 originales. Grados AA–E. 224×224 px. Licencia ODbL/DbCL. **Reserva**, no principal:
semántica ajena y resolución dudosa para grietas.

### 6.3 Encontrados y no utilizables para el mínimo

| Conjunto | Motivo |
| --- | --- |
| Zenodo tactile whole/cracked eggs (DOI 10.5281/zenodo.15360469) | **377** imágenes táctiles 640×480, no RGB de cámara. Licencia CC BY 4.0. Demasiado pequeño y de otro sensor |
| Egg-Instance-Segmentation (Hugging Face, MIT) | Mismas 51 fotos (`sample1`–`sample51`) que Egg-Detection, con polígonos. **No suma imágenes nuevas** |
| Paper JAITA / Food Bioprocess (2.400 imágenes, 400 huevos × 6 vistas: intact, cracked, dirty, bloodstained) | **No hay descarga pública verificada.** Solo descripción en artículos |
| Paper IIETA (1.000 cracked + 1.000 intact) | **No hay descarga pública verificada** |
| Aedes / huevos parásitos (Mendeley, Hugging Face) | No son huevos de gallina de consumo |
| so101-egg-cracking (Hugging Face) | Robótica / demostraciones; no es un conjunto de clasificación de estado de cáscara |

---

## 7. Riesgos de combinar conjuntos

Siguen vigentes los de [`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md) sección 5.2,
ahora con más peso porque el mínimo de 1.000 **empuja** a mezclar fuentes:

1. **Aprender la fuente, no la clase.** Si cada estado viene de un conjunto distinto, el fondo
   predice la etiqueta.
2. **Contar cajas como imágenes.** Egg-Detection tiene 423 cajas y 51 fotos: para el profesor
   cuentan 51.
3. **Contar aumentación como originales.** Good and Bad Eggs: 1.000, no 7.000.
4. **Fuga por grupos.** Varias vistas del mismo huevo (el paper de 6 ángulos, o fotogramas de
   video) no pueden partirse entre train y test.
5. **Duplicados** entre fichas de Roboflow y entre plataformas.
6. **Licencias incompatibles** (ODbL *share-alike*, CC BY-NC, o ausencia de licencia).

Mitigación ya acordada: capturar las **cuatro clases** en el mismo escenario; partición de
prueba propia; registrar el origen de cada imagen.

---

## 8. Necesidad de datos propios

**Obligatoria**, no para inflar el recuento, sino porque:

- `danado` sigue **sin fuente pública descargable**;
- `sucio` sigue **sin fuente con licencia verificada**;
- el escenario de banda simulada no está en Egg-Detection;
- las cuatro clases deben verse con la misma cámara.

Cuántas hay que tomar **depende** de cuánto volumen público usable se confirme. Orden de
magnitud, no cuota:

- si entra un conjunto de detección de ≥ 1.000 con licencia (p. ej. el de Ultralytics, **si**
  se verifica), la captura propia puede ser más pequeña y centrada en escenario + `sucio` +
  `danado`;
- si solo se cuentan INDIGO (840) + Egg-Detection (51) = 891, hacen falta **al menos 109
  imágenes reales adicionales** solo para el detector, más las de estado que falten.

---

## 9. Recomendación

**Detección.** No hay hoy un conjunto principal **con licencia verificada y ≥ 1.000 imágenes**.
El camino verificable más corto es:

1. Conservar Egg-Detection (51) como complementario.
2. Incorporar INDIGO (840) — licencia ya verificada.
3. Completar ≥ 109 imágenes reales (propias y/o un tercero verificado).
4. **En paralelo**, verificar a mano la licencia de `egg_dataset` (Ultralytics, 2.553). Si es
   usable, pasa a ser el **candidato principal** de detección (y aporta `normal`/`cracked`).

**Estado.** Ningún conjunto público cubre las cuatro clases con licencia verificada. Para el
mínimo de 1.000:

- 1.000 originales de Good and Bad Eggs (inspección, no remapeo ciego);
- INDIGO para `grieta`;
- fuentes Roboflow de suciedad **solo** tras verificar licencia;
- captura propia **obligatoria** de las cuatro, y **principal** para `sucio` y `danado`.

**Calibre AAA / criollo / semicriollo:** fuera de esta revisión (siguen experimental / futuro).

---

## 10. Decisión

```
DATASET ACTUAL Egg-Detection:
    SE CONSERVA COMO COMPLEMENTARIO.
    51 imágenes reales, 423 cajas, MIT, YOLO.
    Script y README se mantienen.

DATASET PRINCIPAL DE DETECCIÓN:
    PENDIENTE.

    Candidato a verificar (licencia):
      egg_dataset (Ultralytics / Ahmed Raza)
      2.553 imágenes, cinta industrial, normal + cracked
      https://platform.ultralytics.com/ahmed-raza/datasets/eggdataset

    Camino verificable mientras tanto:
      INDIGO (840, CC BY 4.0) + Egg-Detection (51, MIT) + capturas propias
      = 891 públicas; faltan ≥ 109 reales para el mínimo.

    Volumen de huevos reales con licencia, sin cajas:
      Egg Variety (Mendeley) 9.100 originales, CC BY 4.0
      — solo si se confirma que sirven para detección o se anotan.

DATASETS PARA ESTADO:
    bueno   → Good and Bad Eggs (1.000 originales, CC BY 4.0) [inspección]
            → `normal` de egg_dataset / `normal-egg` Roboflow [PENDIENTE]
    grieta  → INDIGO (840, CC BY 4.0)
            → `cracked` de egg_dataset / Roboflow [PENDIENTE]
    sucio   → DIrty Egg, dirt stained egg, Egg Quality Grading [PENDIENTE licencia]
            → captura propia (fuente principal mientras tanto)
    danado  → NINGUNO público. Captura propia obligatoria.

CAPTURA PROPIA:
    OBLIGATORIA.
    Cuatro clases, mismo escenario.
    No tiene que ser ella sola las 1.000 si hay públicos usables.

REQUISITO FINAL:
    >= 1000 imágenes reales antes del entrenamiento
    (objetivo 1200–2000 si los datos lo permiten).
    El augmentation no cuenta para este mínimo.
```

---

## 11. Estado tras esta revisión

- **No se descargó nada nuevo.**
- **No se entrenó ningún modelo.**
- **No se borró Egg-Detection**, ni su script, ni su README.
- **No se borraron** las decisiones de `docs/06` y `docs/07`; se añadió trazabilidad.
- Licencia **nueva** confirmada: Egg Variety (Mendeley) **CC BY 4.0**.
- Licencia **pendiente** más urgente: Ultralytics `egg_dataset` (2.553 imágenes).

**Siguiente paso:** verificar a mano la licencia y las clases de `egg_dataset` y de las fichas
Roboflow de ≥ 1.000 imágenes; no entrenar hasta que el recuento de imágenes **reales** del
conjunto de entrenamiento sea ≥ 1.000.
