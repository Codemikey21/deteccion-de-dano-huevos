# Conjunto de datos: INDIGO Crack Detection

> **Estado: LISTO PARA EDA.** Descarga y auditoría en disco hechas el 21/09/2026.
> **No se ha entrenado.** No se ha convertido VOC a YOLO. No se ha hecho *preprocessing*.
>
> Dataset **principal inicial**. Posteriormente, el profesor confirmó que un conjunto de al
> menos 800 imágenes es aceptable. Por tanto, INDIGO con **840 imágenes reales** cumple el
> requisito académico. Detalle de la auditoría:
> [`../../../docs/13-validacion-final-indigo.md`](../../../docs/13-validacion-final-indigo.md).

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
| **Verificación de la licencia** | API de figshare, 21/09/2026 |
| **Publicado** | 16/11/2022 |
| **Fecha de descarga** | 21/09/2026 |
| **Fecha de auditoría** | 21/09/2026 |

---

## Cantidades verificadas en disco

| Elemento | Verificado |
| --- | --- |
| Imágenes **reales** | **840** JPEG |
| Train real | **740** (`train/train_100/*.jpg`) |
| Test real | **100** (`test/test_100/*.jpg`) |
| Anotaciones | **840** Pascal VOC XML (740 + 100) |
| Clases | `egg` (838 cajas / 838 imágenes), `crack` (945 cajas / 817 imágenes) |
| JPEG corruptos | **0** |
| XML sin imagen | **0** |
| Imágenes sin XML | **0** |
| Duplicados MD5 (fotos reales) | **0** |
| Resolución principal | **3456 × 4608** (839 fotos; 1 foto en 4608 × 3456) |
| MD5 de los ZIP | correcto (`train.zip` `6bdc229bc98c808ad7ec3f76e0e5feeb`, `test.zip` `0d1bca3b8408cd7114cbcf0c6836c34b`) |

**Hay que ignorar `__MACOSX/` y cualquier archivo `._*`.** Son sidecars de macOS, no
fotografías. El primer conteo del script (1.680 “imágenes”) sumó 840 JPEG reales + 840
`._*.jpg`. **No se borra `__MACOSX/` en este paso**; EDA y *preprocessing* futuros no deben
entrar ahí.

---

## Estructura local (tras extraer)

```
data/raw/indigo/
├── train.zip
├── test.zip
├── train/train_100/     ← JPEG + XML reales (usar esto)
├── train/__MACOSX/      ← ignorar
├── test/test_100/       ← JPEG + XML reales (usar esto)
└── test/__MACOSX/       ← ignorar
```

---

## Formato y clases

- Anotaciones: **Pascal VOC XML**, un `.xml` por `.jpg`, mismo *stem*.
- Clases en los XML: **`egg`** y **`crack`**.
- No es YOLO. La conversión, si hace falta para YOLOv8n, es un paso posterior.

---

## Uso previsto

1. **Detección** de huevos (`egg`).
2. Apoyo a la clase de estado **`grieta`** (`crack`).

No cubre `sucio` ni `danado`. Egg-Detection sigue como complementario. Ahmed Raza
`egg_dataset` sigue **PENDIENTE DE LICENCIA**.

**Siguiente paso técnico:** EDA sobre `train/train_100/` y `test/test_100/`. No entrenar.
