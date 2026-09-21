# Validación de dataset principal de detección

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fecha de consulta: **21 de septiembre de 2026**
Documentos relacionados: [`07-validacion-fuentes-dataset.md`](07-validacion-fuentes-dataset.md) ·
[`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md) ·
[`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)

> **No se ha descargado este conjunto.** No se ha entrenado ningún modelo. Este documento
> valida metadatos y fichas públicas para decidir si
> `Williamsanderson/PoultryVision-Dataset` puede ser el **dataset principal de detección**.

El archivo se numera como `11` porque `docs/10-decision-tecnica-provisional.md` ya existe.

---

## 0. Método de verificación

| Vía | URL / recurso | Resultado (21/09/2026) |
| --- | --- | --- |
| Ficha oficial del dataset (navegador) | https://huggingface.co/datasets/Williamsanderson/PoultryVision-Dataset | **404** — «Sorry, we can't find the page you are looking for.» |
| API de Hugging Face | `https://huggingface.co/api/datasets/Williamsanderson/PoultryVision-Dataset` | **401** — `Invalid username or password.` |
| Árbol de archivos | `.../api/datasets/.../tree/main` | **401** |
| README crudo | `.../raw/main/README.md` | **401** |
| Hugging Face Dataset Server | `https://datasets-server.huggingface.co/info?dataset=Williamsanderson/PoultryVision-Dataset` | **401** — el conjunto «does not exist, or is not accessible without authentication (private or gated)» |
| Listado público del autor | `https://huggingface.co/api/datasets?author=Williamsanderson` | **200**, 5 datasets, **ninguno** es `PoultryVision-Dataset` (solo series MedQA) |
| Control de la misma API | `https://huggingface.co/api/datasets/afshin-dini/Egg-Detection` | **200** — la API funciona; el fallo es de este repositorio, no de Hugging Face en general |
| Ficha pública del **modelo** asociado | https://huggingface.co/Williamsanderson/PoultryVision | **200** |
| `data.yaml` del modelo | mismo repositorio | **200** |
| Gráficas de entrenamiento del modelo (`labels.jpg`, matriz, `val_batch0_pred.jpg`) | mismo repositorio | **200** — no son el dataset; son artefactos del modelo ya publicado |
| Tarjeta del dataset indexada por buscadores | fragmentos de la ficha que existió en Hugging Face | **Parcial** — no sustituye a la ficha viva |

Consecuencia: **hoy no se puede leer `cardData.license` ni contar archivos en la ficha oficial.**
Las cifras de imágenes, splits y clases se contrastan con la ficha **pública del modelo**
entrenado sobre ese conjunto y, en segundo lugar, con la tarjeta indexada. Eso no equivale a
haber abierto el dataset.

No se usó token de Hugging Face. No se descargaron imágenes del dataset.

---

## 1. Ficha del candidato

| # | Campo | Valor verificado | Fuente | Estado |
| --- | --- | --- | --- | --- |
| 1 | Nombre exacto | `PoultryVision Unified Dataset` (repo `Williamsanderson/PoultryVision-Dataset`) | Modelo público; tarjeta indexada | Nombre coincidente. **Repo no listado / no accesible hoy** |
| 2 | URL | https://huggingface.co/datasets/Williamsanderson/PoultryVision-Dataset | Declarada por el usuario y por el modelo | **La URL responde 404** |
| 3 | Autor | Usuario Hugging Face `Williamsanderson`. El modelo cita a **Stephane Williams Anderson ASSA**; la tarjeta indexada firma «Williams Anderson» | Modelo; tarjeta indexada | Coherente; no hay ficha viva que lo confirme |
| 4 | Licencia exacta | Ver sección 2 | — | **No verificada en la ficha viva** |
| 5 | Número de imágenes | **21.586** declaradas (detección) | Modelo: «PoultryVision Unified (21 586 images)»; splits 15.987 + 3.706 + 1.893 = 21.586 | **Declarado, no auditado en árbol de archivos** |
| 6 | Splits | train **15.987** · val **3.706** · test **1.893** | Ficha del modelo, tabla de métricas | Suma correcta. **No auditado** |
| 7 | Clases | `0 = chicken` (broilers, hens, cocks); `1 = egg` (huevos en suelo o nido) | `data.yaml` y tabla de clases del modelo | **Verificado en el yaml del modelo** |
| 8 | Formato de anotación | YOLO / Ultralytics (`path`, `train`/`val`/`test`, `nc`, `names`) | `data.yaml` | **Compatible** |
| 9 | Tamaño | **No publicado** en las vías accesibles | API del dataset inaccesible | **Desconocido** |
| 10 | Procedencia | Fusión de **seis** fuentes públicas (sección 3) | Modelo + tarjeta indexada | Composición declarada; licencias de origen **no verificadas una a una** |

Los datos preliminares del enunciado (21.586, YOLO, clases 0/1, splits, CC BY 4.0) **coinciden
con la ficha del modelo y con la tarjeta indexada**. No coinciden con una lectura actual de la
ficha oficial, porque esa ficha **no está disponible**.

---

## 2. Licencia

### Lo que se pudo leer

La tarjeta **indexada** del dataset (no la página viva) decía:

- «This dataset is released under CC-BY-4.0.»
- El empaquetado unificado, los splits y la armonización de etiquetas son © 2025 Williams
  Anderson, CC BY 4.0.
- **Las fuentes individuales conservan su licencia original:**
  - MVBroTrack (Cardoen et al., 2025) — remitir al artículo y a su *data statement*;
  - conjuntos de Roboflow Universe — «typically CC-BY-4.0 (**check each source**)»;
  - conjuntos de images.cv — CC BY 4.0 / dominio público.
- Hay que citar las fuentes originales si se usan los subconjuntos.

Eso **no** es una licencia única verificada sobre todo el material. Es una licencia del
empaquetado **más** una advertencia de que hay que mirar cada origen.

### Lo que no se pudo leer

- Campo estructurado `cardData.license` de la API de Hugging Face (**401**).
- Archivo `LICENSE` o README vivo del dataset (**401 / 404**).
- Licencia de cada uno de los seis orígenes, ficha por ficha.

### Lo que sí está publicado en el modelo

La ficha de **Williamsanderson/PoultryVision** (el modelo, no el dataset) declara
**AGPL-3.0** para los **pesos**. Eso no transfiere AGPL al dataset, pero tampoco sustituye a
la licencia de las imágenes. Este proyecto **no usaría esos pesos**; el detector previsto es
YOLOv8n entrenado por nosotros
([`10-decision-tecnica-provisional.md`](10-decision-tecnica-provisional.md)).

### Lectura para este proyecto

**CC BY 4.0 no queda verificada como licencia usable de todo el conjunto.** El propio texto
indexado obliga a revisar MVBroTrack, Roboflow e images.cv. Roboflow ya quedó sin verificar
en [`07-validacion-fuentes-dataset.md`](07-validacion-fuentes-dataset.md) por Cloudflare.

---

## 3. Procedencia de los datos

Según `data.yaml` del modelo y la tabla de fuentes de la tarjeta indexada:

| # | Fuente declarada | Tipo declarado | Plataforma |
| --- | --- | --- | --- |
| 1 | Dataset Chicken 1 | Clasificación | images.cv |
| 2 | Dataset Chicken 2 | Clasificación | images.cv |
| 3 | Dataset Chicken 3 | Detección (COCO) | Roboflow Universe |
| 4 | Chickens-Eggs v1 | Detección (YOLOv8) | Roboflow Universe |
| 5 | chicken eggs 2 v3 | Detección + segmentación | Roboflow Universe |
| 6 | MVBroTrack | Seguimiento multi-cámara de pollos de engorde | Cardoen et al., *Computers and Electronics in Agriculture*, 2025 |

El modelo resume el conjunto como «six public poultry datasets (≈21.6 k detection images +
MVBroTrack multi-camera data)» y el escenario como **granjas avícolas** (broilers, gallinas,
gallos y huevos en suelo o nido), no como cinta de clasificación de huevos.

Las fuentes 1–3 son de **gallinas**. Solo 4 y 5 nombran huevos. MVBroTrack es monitoreo de
pollos de engorde en corral, vista cenital.

---

## 4. ¿Hay suficientes huevos? ¿Hace falta filtrar?

### Instancias (cajas), no imágenes

`labels.jpg` del repositorio **del modelo** (artefacto de entrenamiento, no el dataset
descargado) muestra:

| Clase | Instancias anotadas |
| --- | --- |
| `chicken` | **161.411** |
| `egg` | **58.347** |

Hay huevos anotados en volumen alto (**58.347 cajas**). Eso **no** dice cuántas **imágenes**
distintas contienen al menos un huevo. El requisito académico documentado primero era ≥ 1.000 **imágenes reales**, no 1.000 cajas
([`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md)).
Posteriormente, el profesor confirmó que un conjunto de al menos 800 imágenes es aceptable.
Por tanto, INDIGO con 840 imágenes cumple el requisito académico.

La proporción de cajas es ~73 % gallina / ~27 % huevo. El riesgo de que **muchas imágenes sean
solo gallinas** es alto y está respaldado por:

1. Tres de seis fuentes son datasets de pollo.
2. MVBroTrack es un corral de pollos de engorde.
3. `val_batch0_pred.jpg` del modelo muestra **nueve fotogramas cenitales de nave**, densos en
   cajas `chicken`. En ese lote **no aparece ninguna caja `egg`**.

### Filtrado

**Sí haría falta filtrar** antes de usarlo como detector de clase única `egg`:

- quedarse solo con imágenes que tengan al menos una caja `egg`;
- ignorar o no entrenar la clase `chicken` (nuestro detector no debe aprender gallinas);
- no contar las 21.586 imágenes como si todas fueran de huevos.

Hasta no poder listar etiquetas, **no se puede afirmar** que el subconjunto con huevos
supere el umbral académico vigente (800 imágenes). Es plausible por el número de cajas `egg`,
y **no está demostrado**.

### Escenas de producción

**Sí hay escenas reales de producción avícola** (nave, cama, comedero, cámara cenital). **No**
son el escenario de nuestro MVP (huevos pasando frente a una cámara, simulando banda). El
huevo aparece, según el modelo, «ground or in nest». Eso es dominio distinto al de
Egg-Detection (bandeja) y al de Ahmed Raza (cinta industrial).

---

## 5. Compatibilidad con YOLOv8

| Aspecto | Evaluación |
| --- | --- |
| Formato de etiquetas | YOLO Ultralytics (`nc: 2`, `names` indexados). YOLOv8 lee el mismo `data.yaml` |
| Splits | `train` / `val` / `test` ya declarados |
| Entrenamiento previsto del proyecto | YOLOv8n en Colab, decisión técnica provisional, **no ejecutada** |
| Modelo publicado PoultryVision | YOLOv11m, AGPL-3.0. **No es nuestro detector y no se usaría** |

La incompatibilidad no es de formato. Es de **acceso, licencia de orígenes, filtrado de
clase y dominio visual**.

El `data.yaml` publicado apunta a una ruta local del autor
(`c:/Users/HP/Downloads/Dataset Model Firm/PoultryVision/dataset`). Habría que reescribir
`path` si algún día se descargara. Eso no se hace ahora.

---

## 6. Comparación con los conjuntos ya documentados

| Criterio | PoultryVision-Dataset | Egg-Detection (`afshin-dini`) | INDIGO (figshare) | `egg_dataset` (Ahmed Raza) |
| --- | --- | --- | --- | --- |
| URL viva | **404 / 401** | Accesible | Accesible (DOI) | Ficha Ultralytics accesible; **sin licencia en la ficha** |
| Imágenes reales | 21.586 **declaradas**, no auditadas | **51** auditadas | **840** | **2.553** declaradas |
| ¿Cubre ≥ 800 sola? (umbral vigente) | Solo si el subconjunto `egg` lo cubre; **no medido** | No | **Sí** (840) | Sí en volumen, si la licencia fuera usable |
| Licencia | CC BY 4.0 **del empaquetado**, orígenes por verificar | **MIT** verificada (API HF) | **CC BY 4.0** verificada (API figshare) | **PENDIENTE DE LICENCIA** |
| Formato | YOLO | YOLO | Cajas `egg` / `crack` | Detección de objetos |
| Clases | `chicken`, `egg` | Huevos (nombres finales no leídos en `data.yaml`) | `egg`, `crack` | `normal`, `cracked` |
| Escenario | Granja / nido / suelo | Bandeja o cartón | Inspección de grietas | Cinta industrial |
| ¿Principal de detección hoy? | **No** | Complementario | **Principal inicial** (cumple ≥ 800) | Candidato técnico **pendiente de licencia** |
| Descargado | No | No | No | No |

Frente a Egg-Detection e INDIGO, PoultryVision gana en **volumen declarado**. Pierde en
**acceso actual**, en **licencia cerrada** y en **ajuste al escenario de huevos en línea**.

Frente a Ahmed Raza, Ahmed Raza sigue más cerca del escenario del proyecto (cinta,
`normal`/`cracked`) y sigue bloqueado **solo** por licencia. PoultryVision está bloqueado por
**acceso + licencia de orígenes + filtrado de gallinas + dominio**.

---

## 7. Riesgos si se usara más adelante

1. **El repositorio no es público hoy.** Puede estar privado, gated o eliminado. No hay
   descarga posible sin que el autor lo vuelva a publicar.
2. **Licencia compuesta.** Aprobar «CC BY 4.0» sin revisar MVBroTrack, Roboflow e images.cv
   contradiría el criterio de [`07-validacion-fuentes-dataset.md`](07-validacion-fuentes-dataset.md).
3. **Aprender gallinas, no huevos.** Entrenar las 21.586 imágenes sin filtrar enseñaría
   `chicken` como clase dominante.
4. **Desajuste de dominio.** Nave cenital ≠ banda / bandeja / cámara de iPhone del MVP.
5. **Clasificación de estado.** Este conjunto no cubre `bueno` / `grieta` / `sucio` /
   `danado`. No sustituye a INDIGO ni a la captura propia de estado.
6. **Contar cajas como imágenes.** 58.347 cajas `egg` no son 58.347 fotografías.

---

## 8. Decisión

```
CANDIDATO: Williamsanderson/PoultryVision-Dataset
VEREDICTO: PENDIENTE

NO APROBADO COMO PRINCIPAL.
NO DESCARTADO: el volumen declarado y el formato YOLO siguen siendo atractivos
si el repo vuelve a ser público y se verifican orígenes + recuento de imágenes con huevo.

BLOQUEADO POR:
  1. Ficha oficial inaccesible (404 / 401; no aparece en el listado del autor).
  2. Licencia CC BY 4.0 no verificada en API; orígenes con licencias propias.
  3. Recuento de imágenes que contienen huevos: desconocido.
  4. Dominio de granja/gallina, no de clasificación de huevos en línea.

REPARTO ACTUAL (docs/09 sección 12; umbral vigente ≥ 800):
  INDIGO                = PRINCIPAL INICIAL (840, CC BY 4.0; cumple el requisito)
  Egg-Detection         = complementario (51, MIT)
  PoultryVision-Dataset = PENDIENTE (no principal)
  egg_dataset Ahmed Raza = CANDIDATO TÉCNICO — PENDIENTE DE LICENCIA

NO DESCARGAR.
NO ENTRENAR.
```

**Siguiente paso (si se insiste en este conjunto):** esperar a que el repositorio sea
público, leer `cardData.license` y el árbol de archivos, y **solo entonces** contar cuántas
imágenes tienen al menos una caja `egg`. El dataset principal inicial vigente es INDIGO;
Ahmed Raza sigue pendiente de licencia.
