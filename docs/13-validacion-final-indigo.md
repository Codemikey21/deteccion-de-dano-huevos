# Validación final: INDIGO Crack Detection

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fecha de la auditoría en disco: **21 de septiembre de 2026**
Documentos relacionados: [`07-validacion-fuentes-dataset.md`](07-validacion-fuentes-dataset.md) ·
[`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md) ·
[`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)

> **No se ha entrenado ningún modelo.** No se ha convertido Pascal VOC a YOLO. No se ha
> hecho *preprocessing*. No se ha borrado `__MACOSX/`. Este documento registra la
> inspección del material ya descargado en `data/raw/indigo/`.

El archivo se numera como `13` porque `docs/10` y `docs/11` ya existen.

---

## 1. Fuente

| Campo | Valor |
| --- | --- |
| Nombre | Dataset for real-time crack detection on chicken eggs |
| Nombre corto | INDIGO Crack Detection |
| Autores | Bhavya Botta; Ashis Kumar Datta |
| Publicación | figshare, 16/11/2022 |
| URL | https://doi.org/10.6084/m9.figshare.21568425.v1 |
| DOI | 10.6084/m9.figshare.21568425.v1 |
| Artículo figshare | `21568425`, versión 1 |
| Destino local | `data/raw/indigo/` |
| Script de descarga | `scripts/download_indigo_dataset.py` |
| ZIP oficiales | `train.zip` (MD5 `6bdc229bc98c808ad7ec3f76e0e5feeb`) y `test.zip` (MD5 `0d1bca3b8408cd7114cbcf0c6836c34b`) |

En los metadatos de figshare `test.zip` aparece dos veces con el mismo tamaño y el mismo MD5.
Se descargó **un** archivo.

Papel en el proyecto: **dataset principal inicial** de detección. Posteriormente, el profesor
confirmó que un conjunto de al menos 800 imágenes es aceptable. Por tanto, INDIGO con 840
imágenes reales cumple el requisito académico.

---

## 2. Licencia

**CC BY 4.0.**

Verificada el 21/09/2026 en la API de figshare (`license.name` = `CC BY 4.0`,
`license.url` = https://creativecommons.org/licenses/by/4.0/). Uso académico permitido con
atribución a los autores y al DOI.

---

## 3. Cantidad real de imágenes

**840 fotografías reales** (JPEG), todas con nombre `IMG_YYYYMMDD_HHMMSS.jpg`.

| Qué cuenta | Qué no cuenta |
| --- | --- |
| `train/train_100/*.jpg` (740) | `__MACOSX/**/._*.jpg` |
| `test/test_100/*.jpg` (100) | archivos `._*` y `.DS_Store` |

El primer conteo automático del downloader (1.680) **no** es el número de fotografías. Ver
secciones 11 y 12.

---

## 4. Partición original train / test

| Split | Carpeta | Imágenes reales | Anotaciones XML |
| --- | --- | --- | --- |
| train | `data/raw/indigo/train/train_100/` | **740** | **740** |
| test | `data/raw/indigo/test/test_100/` | **100** | **100** |
| validation | — | **no existe** | — |
| **Total** | | **840** | **840** |

Se conserva la partición del origen. **No** se crea aquí un `val`.

---

## 5. Formato de anotación: Pascal VOC

Las etiquetas son **Pascal VOC XML** (`<annotation>`), no YOLO.

Cada fotografía tiene un `.xml` con el mismo *stem*. Campos observados: `filename`, `path`,
`size` (width, height, depth), `segmented` = 0, y uno o más `object` con `name` y `bndbox`
(`xmin`, `ymin`, `xmax`, `ymax`).

No hay máscaras (`segmented` = 0 en los 840 XML). **No se convierte a YOLO en este paso.**

---

## 6. Clases reales

Leídas de los 840 XML. Solo aparecen estas dos cadenas:

| Clase | Instancias (cajas) | Imágenes que la contienen |
| --- | --- | --- |
| `egg` | 838 | 838 |
| `crack` | 945 | 817 |

No hay IDs numéricos ni otras etiquetas. 2 imágenes tienen solo `crack`; 23 tienen solo `egg`.

---

## 7. Número de anotaciones

**840 archivos XML**, uno por imagen real.

- JPEG sin XML: **0**
- XML sin JPEG: **0**
- Errores al parsear XML: **0**
- Cajas fuera de la imagen o con `xmin ≥ xmax` / `ymin ≥ ymax`: **0**

Cajas por imagen: 1 (23 fotos), 2 (709), 3 (92), 4 (14), 5 (2).

---

## 8. Integridad

| Comprobación | Resultado |
| --- | --- |
| JPEG reales ilegibles (sin SOI / SOF / EOI) | **0** |
| Archivos vacíos | **0** |
| MD5 de `train.zip` y `test.zip` | coinciden con figshare |
| Tamaño declarado en el XML vs. cabecera JPEG | **0** desajustes |
| `__MACOSX` y `._*` | presentes; **no** son imágenes; **no** se borran en este paso |

---

## 9. Resoluciones

Medidas en la cabecera SOF de los 840 JPEG reales:

| Resolución (ancho × alto) | Imágenes |
| --- | --- |
| **3456 × 4608** | **839** |
| 4608 × 3456 | 1 (misma captura, girada) |

Tamaño de archivo: mínimo 1,94 MiB, mediana 2,61 MiB, máximo 4,81 MiB, media ≈ 2,73 MiB.

---

## 10. Duplicados

MD5 de las **840** fotografías reales: **0 grupos duplicados**. Cada JPEG es distinto.

Los 840 `._*.jpg` no son copias de las fotos: pesan 212–268 bytes, empiezan por la magia
AppleDouble `00 05 16 07` (`Mac OS X`) y su MD5 no coincide con el del JPEG emparejado.

---

## 11. El problema `__MACOSX`

Los ZIP se empaquetaron en macOS. Al extraer aparecen:

```
train/__MACOSX/train_100/._IMG_….jpg
train/__MACOSX/train_100/._IMG_….xml   (solo 68 de 740)
test/__MACOSX/test_100/._IMG_….jpg
test/__MACOSX/test_100/._IMG_….xml
```

Son **sidecars AppleDouble**: metadatos de recurso (icono, atributos), no fotografías ni
anotaciones. Deben **ignorarse** en EDA y en cualquier *preprocessing* futuro.

**No se borran en este paso.** Siguen en disco.

---

## 12. Por qué 1.680 no eran 1.680 fotografías

El script de descarga cuenta como imagen cualquier archivo con extensión `.jpg` (y similares),
sin excluir `__MACOSX/` ni nombres `._*`.

| | train | test | total |
| --- | --- | --- | --- |
| JPEG reales | 740 | 100 | **840** |
| Sidecars `._*.jpg` | 740 | 100 | 840 |
| Contados por el script | 1480 | 200 | **1680** |

1680 = 840 fotos + 840 sidecars. Es exactamente el doble por eso, no porque el conjunto tenga
1.680 escenas.

---

## 13. Limitaciones

- Solo dos clases: `egg` y `crack`. **No cubre** `sucio` ni `danado`.
- No hay partición `validation`.
- Anotación en Pascal VOC; YOLOv8n (decisión técnica provisional) exigirá una conversión
  **posterior**, no hecha aquí.
- Escenario de inspección de grietas, no de banda / Expo Go.
- Dos imágenes sin caja `egg`; 23 sin caja `crack`.
- Fotografías grandes (~2,7 MiB, 3456×4608): hay que tenerlo en cuenta en EDA y más adelante
  al entrenar.
- El conteo automático del downloader no distingue sidecars; EDA debe restringirse a
  `train/train_100/` y `test/test_100/`.

Egg-Detection (51, MIT) sigue como complementario. `egg_dataset` (Ahmed Raza) sigue
**PENDIENTE DE LICENCIA**.

---

## 14. Estado final

```
INDIGO Crack Detection
    840 imágenes reales (740 train / 100 test)
    840 anotaciones Pascal VOC XML
    clases: egg, crack
    licencia: CC BY 4.0
    integridad: 0 JPEG corruptos, 0 XML huérfanos, 0 JPEG sin XML, 0 duplicados MD5
    __MACOSX / ._* : sidecars; se ignoran; no se borran todavía

ESTADO: LISTO PARA EDA.

NO ENTRENAR.
NO CONVERTIR VOC → YOLO EN ESTE PASO.
NO HACER PREPROCESSING EN ESTE PASO.
```
