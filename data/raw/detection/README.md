# Conjunto de datos: detección de huevos

> **Estado: PENDIENTE DE EJECUCIÓN.** La descarga todavía no se ha ejecutado. Esta carpeta
> contiene únicamente este archivo. Las cantidades marcadas como *verificadas* se completarán
> después de ejecutar `scripts/download_detection_dataset.py`.
>
> **Requisito académico (añadido después):** el entrenamiento exigía ≥ 1.000 imágenes reales.
> Este conjunto tiene 51 imágenes y se conserva como **complementario**, no como fuente principal.
> Posteriormente, el profesor confirmó que un conjunto de al menos 800 imágenes es aceptable.
> Por tanto, INDIGO con 840 imágenes cumple el requisito académico y es el dataset principal
> inicial. Ver
> [`../../../docs/09-revision-datasets-requisito-1000.md`](../../../docs/09-revision-datasets-requisito-1000.md),
> sección 12.

---

## Identificación

| Campo | Valor |
| --- | --- |
| **Nombre** | Egg-Detection |
| **Identificador** | `afshin-dini/Egg-Detection` |
| **Fuente** | Hugging Face Datasets |
| **Autor** | `afshin-dini` |
| **URL** | https://huggingface.co/datasets/afshin-dini/Egg-Detection |
| **Licencia** | **MIT** |
| **Verificación de la licencia** | API de Hugging Face, campo `cardData.license` = `mit`, consultada el 21/09/2026 |
| **Revisión solicitada** | `main` |
| **Commit real descargado** | PENDIENTE DE EJECUCIÓN |
| **Fecha de descarga** | PENDIENTE DE EJECUCIÓN |

## Clases originales

**PENDIENTE DE VERIFICACIÓN.**

La ficha del conjunto sugiere dos clases por color de cáscara. Los nombres exactos y su orden
numérico están en `data/data.yaml`, que **todavía no se ha leído**. Hasta entonces **no se afirma**
que las clases sean `white-egg` y `brown-egg`.

Cuando se confirmen, el plan es fusionarlas en nuestra clase única `egg`: el color de la cáscara
no aporta información al problema de localizar el huevo. Esa fusión tampoco se aplica todavía.

## Formato

| Campo | Valor |
| --- | --- |
| Tipo de tarea | Detección de objetos |
| Anotaciones | YOLO: un archivo `.txt` por imagen, con una línea por caja |
| Imágenes | JPG |
| Configuración | `data/data.yaml`, más los listados `data/train.txt` y `data/val.txt` |
| Estructura | `data/images/{train,val}/` y `data/labels/{train,val}/` |

La estructura original se conserva **tal cual**, con una única excepción: el conjunto trae su
propio `README.md` en la raíz, que colisionaría con este archivo de documentación. El script lo
guarda como **`_origen_README.md`**, de modo que se conservan los dos.

El script **no crea** particiones nuevas. La división original (49 `train` / 2 `val`) **no es
adecuada para una validación seria**. Una nueva división `train` / `validation` / `test` se
hará más adelante, durante la preparación del conjunto.

## Contenido declarado por el origen

Datos obtenidos de la API de árbol de archivos de Hugging Face
(`/api/datasets/afshin-dini/Egg-Detection/tree/main?recursive=true`), consultada el 21/09/2026.
**No son cantidades verificadas localmente**, sino lo que el origen declara:

| Elemento | Cantidad declarada |
| --- | --- |
| Archivos totales | 108 |
| Imágenes `.jpg` | **51** |
| Archivos de etiquetas `.txt` | 51 |
| Imágenes en `train` | 49 |
| Imágenes en `val` | 2 |
| Cajas anotadas | **423** (393 en `train`, 30 en `val`; inferidas del tamaño de los `.txt`) |
| Otros archivos | `data.yaml`, `train.txt`, `val.txt`, `dataset.py`, `README.md` (se guarda como `_origen_README.md`), `.gitattributes` |
| Tamaño total | 355.957.082 bytes = **339,47 MiB** ≈ **355,96 MB** |
| Tamaño medio por imagen | ≈ 6,7 MiB |

> **423 no es el número de imágenes.** Es el número total de bounding boxes. La ficha de Hugging
> Face anuncia «423 filas»; esas filas corresponden a instancias anotadas, no a fotografías.

## Cantidad de archivos verificada

**PENDIENTE DE EJECUCIÓN.**

Se completará tras ejecutar el script. Campos a rellenar:

| Elemento | Verificado en disco |
| --- | --- |
| Archivos totales | PENDIENTE DE EJECUCIÓN |
| Imágenes | PENDIENTE DE EJECUCIÓN |
| Etiquetas | PENDIENTE DE EJECUCIÓN |
| Cajas anotadas | PENDIENTE DE EJECUCIÓN |
| Tamaño ocupado | PENDIENTE DE EJECUCIÓN |
| Commit | PENDIENTE DE EJECUCIÓN |
| Verificación de integridad | PENDIENTE DE EJECUCIÓN |

## Uso previsto

Entrenamiento del **detector de huevos** del MVP: localizar huevos en un fotograma y devolver
caja delimitadora y confianza, con la clase única `egg`.

**No se usa para clasificar el estado** (`bueno`, `grieta`, `sucio`, `danado`). Este conjunto no
contiene esa información.

Según [`../../../docs/07-validacion-fuentes-dataset.md`](../../../docs/07-validacion-fuentes-dataset.md),
es uno de los tres conjuntos con licencia verificada y aprobados para descarga. Sirve como
**línea base** de detección; **no basta por sí solo**.

## Observaciones

**1. Volumen pequeño de imágenes, más objetos anotados.** 51 fotografías con 423 cajas. Hay
pocas escenas distintas, pero bastantes instancias de huevo. Es un baseline utilizable, no una
fuente única. El dataset principal inicial es INDIGO (840 imágenes, CC BY 4.0). Este conjunto
sigue como complementario.

**2. La partición `val` original es inutilizable: 2 imágenes.** No permite validar nada. Se
rehará la división `train` / `validation` / `test` en la preparación del conjunto, respetando la
regla de agrupación por huevo físico de
[`../../../docs/03-estrategia-dataset.md`](../../../docs/03-estrategia-dataset.md). **No se crea
ninguna partición todavía.**

**3. Las imágenes son muy pesadas: unos 6,7 MiB cada una.** Sugiere fotografías a resolución
completa de cámara. Es una ventaja para recortar huevos individuales, pero obligará a
redimensionar antes de entrenar. Ese redimensionado se hará en `data/processed/`, **nunca sobre
estos archivos**.

**4. Escenario distinto al nuestro.** Son huevos en bandeja y en caja de cartón, no sobre una
banda transportadora. La partición de prueba debe incluir imágenes propias.

**5. Obligación de atribución.** La licencia MIT exige conservar el aviso de licencia y la
atribución al autor en cualquier uso o redistribución.

## Reproducción

```bash
python scripts/download_detection_dataset.py --dry-run   # consultar sin descargar
python scripts/download_detection_dataset.py             # descargar
python scripts/download_detection_dataset.py --verify-only --check-hash
```

El contenido de esta carpeta **no se versiona en Git** (ver `.gitignore`). Solo se versiona este
README. El material se reconstruye ejecutando el script.
