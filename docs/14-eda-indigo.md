# EDA de INDIGO Crack Detection

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fecha: 21 de septiembre de 2026
Documentos relacionados: [`13-validacion-final-indigo.md`](13-validacion-final-indigo.md) ·
[`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)

> **No se entrenó ningún modelo.** No se convirtió Pascal VOC a YOLO. No se modificaron
> imágenes ni XML. `__MACOSX/` no se borró.

Entregable principal: [`notebooks/01_eda_indigo.ipynb`](../notebooks/01_eda_indigo.ipynb).  
Script reproducible: `python scripts/analyze_indigo_dataset.py --seed 42`.  
Figuras: `evaluation/eda/`.

---

## Metodología

Se leyeron solo `data/raw/indigo/train/train_100/` y `data/raw/indigo/test/test_100/`. Se
ignoraron `__MACOSX/`, `._*`, `.DS_Store` y los ZIP. Cada XML Pascal VOC aportó las cajas
`egg` y `crack`. Semilla 42 para las muestras. El brillo se midió en 80 miniaturas, no en las
840 fotos a resolución nativa.

---

## Resultados principales

| Métrica | Valor medido |
| --- | --- |
| Imágenes reales | **840** (740 train / 100 test) |
| Anotaciones XML | **840** (emparejadas 1:1) |
| Instancias | **1783** (838 `egg`, 945 `crack`) |
| Imágenes con ambas / solo egg / solo crack | 815 / 23 / **2** |
| Objetos por imagen | media 2,12 · mediana 2 · min 1 · max 5 |
| Resolución | 839 × **3456×4608** (retrato); 1 × 4608×3456 |
| Cajas fuera o degeneradas | **0** |
| XML rotos / JPEG sin XML / XML sin JPEG | **0** |
| Cajas `crack` con área relativa < 0,001 | **27** |
| Área relativa mediana | egg **0,223** · crack **0,015** |
| IoU medio egg–crack (941 pares) | 0,12 (mediana 0,06) |

Train y test se parecen: ~2,1 objetos/imagen, ~99 % de fotos con `egg`, área relativa media de
caja 0,123 vs 0,133. Test tiene `crack` en el 100 % de sus 100 fotos.

El fondo de las muestras es mesa oscura + huevo claro centrado, a menudo con una barra. El
brillo de la muestra de 80 miniaturas fue 73 ± 9 (escala 0–255): poca variación lumínica.

---

## Problemas encontrados

1. **`crack` es pequeño** frente a `egg`. Cientos de grietas ocupan < 1 % del fotograma. Con
   YOLOv8n a 640 px esas cajas se vuelven de pocos píxeles.
2. **No hay `validation`.** Solo train/test originales.
3. **Dominio distinto al MVP:** no es banda ni cámara de iPhone.
4. **Cajas anidadas:** la grieta vive dentro del huevo (IoU bajo-moderado, no error).
5. **`__MACOSX`** sigue en disco; un listado ingenuo de `.jpg` vuelve a contar 1.680 archivos.

No hay fotos corruptas ni duplicados MD5 entre las 840 reales (ya auditado en
[`13-validacion-final-indigo.md`](13-validacion-final-indigo.md)).

---

## Decisiones derivadas

- INDIGO **sigue LISTO PARA EDA** y sigue siendo el dataset principal inicial.
- **No se convierte VOC→YOLO en este paso.**
- **No se entrena.**
- Un `val` propio se definirá al preparar el conjunto para YOLO, sacándolo de train, sin
  tocar test.
- El *augmentation* (escala, mosaic, brillo) se considerará en entrenamiento, no ahora, y
  apunta sobre todo a `crack`.
- `__MACOSX/` se **ignora**; no se borra todavía.

---

## Siguiente paso recomendado

Convertir las 840 anotaciones VOC a YOLO **excluyendo** sidecars, documentar el mapeo
`egg`/`crack` → clases del detector/clasificador, y proponer el split `val`. **Sin entrenar.**
