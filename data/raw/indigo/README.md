# Conjunto de datos: INDIGO Crack Detection

> **Estado: PENDIENTE DE EJECUCIÓN.** La descarga todavía no se ha ejecutado. Esta carpeta
> contiene únicamente este archivo. Las cantidades marcadas como *verificadas* se completarán
> después de ejecutar `scripts/download_indigo_dataset.py`.
>
> **Uso vigente:** dataset **principal inicial** de detección. Posteriormente, el profesor
> confirmó que un conjunto de al menos 800 imágenes es aceptable. Por tanto, INDIGO con 840
> imágenes cumple el requisito académico. Ver
> [`../../../docs/09-revision-datasets-requisito-1000.md`](../../../docs/09-revision-datasets-requisito-1000.md),
> sección 12.

---

## Identificación

| Campo | Valor |
| --- | --- |
| **Nombre** | Dataset for real-time crack detection on chicken eggs |
| **Nombre corto** | INDIGO Crack Detection |
| **Autores** | Bhavya Botta; Ashis Kumar Datta |
| **Fuente** | figshare (INDIGO, University of Illinois at Chicago) |
| **URL** | https://doi.org/10.6084/m9.figshare.21568425.v1 |
| **DOI** | 10.6084/m9.figshare.21568425.v1 |
| **Identificador figshare** | artículo `21568425`, versión 1 |
| **Licencia** | **CC BY 4.0** |
| **Verificación de la licencia** | API de figshare, `license.name` = `CC BY 4.0`, `license.url` = https://creativecommons.org/licenses/by/4.0/ ; consultada el 21/09/2026 |
| **Publicado** | 16/11/2022 |
| **Fecha de consulta de metadatos** | 21/09/2026 |
| **Fecha de descarga** | PENDIENTE DE EJECUCIÓN |

## Contenido declarado por el origen

Datos de la descripción oficial y de la API de figshare (`/v2/articles/21568425`),
consultada el 21/09/2026. **No son cantidades verificadas en disco.**

| Campo | Valor declarado |
| --- | --- |
| Imágenes | **840** |
| Split train | **740** |
| Split test | **100** |
| Clases | `egg` y `crack` |
| Formato de anotación | **PENDIENTE DE EJECUCIÓN** (la ficha no lo detalla; se leerá tras extraer) |
| ZIP oficiales | `train.zip` (1.948.036.678 bytes, MD5 `6bdc229bc98c808ad7ec3f76e0e5feeb`) y `test.zip` (266.920.567 bytes, MD5 `0d1bca3b8408cd7114cbcf0c6836c34b`) |
| Duplicado en metadatos | `test.zip` aparece **dos veces** con el mismo tamaño y el mismo MD5 (ids `38230539` y `38230545`). El script descarga **uno** solo |
| Tamaño de los ZIP | 2.214.957.245 bytes ≈ **2,06 GiB** (la ficha se redondeaba a ~2,5 GB) |

## Cantidad de archivos verificada

**PENDIENTE DE EJECUCIÓN.**

| Elemento | Verificado en disco |
| --- | --- |
| Imágenes totales | PENDIENTE DE EJECUCIÓN |
| Imágenes train | PENDIENTE DE EJECUCIÓN |
| Imágenes test | PENDIENTE DE EJECUCIÓN |
| Clases reales | PENDIENTE DE EJECUCIÓN |
| Formato de anotaciones | PENDIENTE DE EJECUCIÓN |
| Tamaño ocupado | PENDIENTE DE EJECUCIÓN |
| MD5 de los ZIP | PENDIENTE DE EJECUCIÓN |

## Uso previsto

Dataset **principal inicial** para:

1. **Detección** de huevos, clase `egg` (módulo 1, YOLOv8n — decisión técnica provisional, no entrenada).
2. **Estado `grieta`**, clase `crack` del mismo conjunto.

**No cubre** `sucio` ni `danado`. **No** se usa todavía para entrenar: falta descargar e
inspeccionar.

Egg-Detection (`data/raw/detection/`) se conserva como **complementario**. Ahmed Raza
`egg_dataset` sigue **PENDIENTE DE LICENCIA**.

## Validación esperada (después de la descarga real)

No ejecutar esta lista hasta haber descargado. Entonces hay que comprobar:

| Comprobación | Esperado |
| --- | --- |
| Número de imágenes | exactamente **840** |
| Split train | **740** |
| Split test | **100** |
| Clases reales | las que existan en las anotaciones (declaradas `egg` y `crack`) |
| Formato de anotaciones | el que traiga el origen (YOLO, COCO u otro); no se convierte en este paso |
| Imágenes corruptas | ninguna ilegible |
| Etiquetas faltantes | cada imagen de train/test con su anotación, o registro de las que no la tengan |
| Distribución por clase | conteo de `egg` y `crack` (cajas o imágenes, según el formato) |
| Resolución | ancho × alto de una muestra; no se redimensiona nada |
| Consistencia de anotaciones | cajas dentro de la imagen; clase conocida; sin archivos de etiqueta huérfanos |

Hasta entonces, todos esos campos quedan como **PENDIENTE DE EJECUCIÓN**.

## Observaciones

1. **Requisito académico vigente: ≥ 800 imágenes reales.** INDIGO declara 840. Cumple. No se
   busca más dataset por cantidad ni se prepara captura propia para completar un mínimo.
2. La partición original es train/test, **sin validation**. Una partición de validación, si hace
   falta, se definirá más adelante. Este script **no** la crea.
3. Extraer los ZIP no modifica los bytes de las imágenes. Transformar, reetiquetar o entrenar
   queda fuera de este paso.
