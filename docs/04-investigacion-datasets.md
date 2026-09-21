# Investigación de conjuntos de datos públicos

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase 1, subpaso 2: investigar conjuntos de datos públicos reales
Fecha de consulta: **21 de septiembre de 2026**
Documentos relacionados: [`03-estrategia-dataset.md`](03-estrategia-dataset.md) ·
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md)

> **No se ha descargado ningún conjunto de datos.** Este documento recoge únicamente lo que
> las fuentes publican en sus páginas públicas. Los conteos, clases y licencias que aparecen
> aquí **no han sido verificados descargando el material**, y deberán confirmarse en el momento
> de la descarga.

---

## 0. Método y limitaciones de esta investigación

**Qué se hizo.** Búsqueda en Roboflow Universe, Kaggle, Mendeley Data, Hugging Face,
repositorios académicos y literatura publicada, con consulta de las fichas públicas de cada
conjunto de datos.

**Limitaciones que hay que tener presentes al leer este documento:**

1. **Roboflow Universe y Kaggle bloquean el acceso automatizado** (Cloudflare y reCAPTCHA
   respectivamente). Los datos de sus fichas se obtuvieron a través de resultados de búsqueda
   que reproducen el contenido de esas páginas. Deben reconfirmarse abriendo cada ficha
   manualmente en un navegador.
2. **Las fichas de Roboflow Universe no siempre indican licencia, resolución ni condiciones de
   captura.** Cuando no aparece, este documento escribe "No especificado por la fuente".
3. **Los conteos de imágenes cambian**: varios proyectos siguen recibiendo versiones nuevas.
   Las cifras corresponden a la fecha de consulta.
4. **Un conjunto de datos publicado no garantiza calidad.** Varias fichas revisadas no tienen
   descripción, tienen clases con nombres sin sentido o contienen solo una parte del material
   etiquetado. Esos casos se señalan expresamente.
5. **No se ha inspeccionado ninguna imagen.** Todo juicio sobre fondos, iluminación o calidad de
   anotación que aparezca aquí es una hipótesis derivada de la descripción, no una observación.

---

## 1. Conjuntos de datos para **detección** de huevos

### 1.1 Egg-Detection (Hugging Face)

| Campo | Valor |
| --- | --- |
| Nombre | Egg detection dataset |
| Fuente | Hugging Face Datasets (autor: afshin-dini) |
| URL | https://huggingface.co/datasets/afshin-dini/Egg-Detection |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | 423 filas; 356 MB en total |
| Clases | `white-egg`, `brown-egg` |
| Formato de anotación | YOLOv5 (carpetas `train`/`val` con `labels`, más `data.yaml`) |
| Licencia | **MIT** |
| Código asociado | https://github.com/afshindini/Deep-Egg-Detection-and-Counter |

**Ventajas.** Es el único candidato de detección con **licencia explícita y permisiva** (MIT)
confirmada en su propia ficha. Formato YOLO listo para usar. El autor indica que las imágenes se
recogieron con distintos tipos y colores de bandeja (plástico transparente, cartón claro y
oscuro) precisamente para dar robustez frente al fondo. Cada imagen contiene varios huevos, por
lo que el número de cajas anotadas es bastante mayor que el número de imágenes.

**Limitaciones.** Pocas imágenes. Las escenas son huevos en bandeja o caja, **no en banda
transportadora**. Solo trae división en `train` y `val`: no hay partición de prueba, habría que
construirla. Las dos clases son por color de cáscara, no por estado.

**Utilidad.** Alta como base para el detector de una sola clase: se pueden fusionar `white-egg`
y `brown-egg` en nuestra clase única `egg`. La licencia MIT elimina el riesgo legal.

### 1.2 egg detection final (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | egg detection final |
| Fuente | Roboflow Universe (autor: egg detection) |
| URL | https://universe.roboflow.com/egg-detection-mnb0n/egg-detection-final |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | 604 |
| Clases | No especificado por la fuente en la ficha consultada |
| Formato de anotación | Exportable desde Roboflow (YOLO TXT, COCO JSON, Pascal VOC XML, TFRecord y otros) |
| Licencia | CC BY 4.0 |
| Publicado | Agosto de 2023 · 110 descargas · 2 estrellas |

**Ventajas.** Licencia clara. Exportación directa en varios formatos. Tiene un modelo YOLOv8s
entrenado asociado, lo que sugiere que las anotaciones son utilizables.

**Limitaciones.** **La ficha no publica descripción ni lista de clases**, así que no se sabe qué
contienen exactamente las imágenes hasta abrir el proyecto. Sin información sobre resolución,
fondo ni condiciones de captura.

**Utilidad.** Media-alta como complemento del anterior, condicionada a revisar las clases.

### 1.3 Egg-count-detection-1 (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | Egg-count-detection- 1 |
| Fuente | Roboflow Universe (autor: Data science) |
| URL | https://universe.roboflow.com/data-science-devhu/egg-count-detection-1 |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | No especificado por la fuente |
| Clases | `Egg` (una sola clase) |
| Formato de anotación | Exportable desde Roboflow |
| Licencia | No especificado por la fuente |
| Publicado | Agosto de 2023 |

**Ventajas.** **Es el único encontrado cuya descripción menciona explícitamente el escenario de
banda transportadora**, que es exactamente el nuestro. Además usa una única clase `Egg`,
idéntica al esquema que definimos en la estrategia.

**Limitaciones.** No publica ni el número de imágenes ni la licencia. El escenario declarado es
conteo en línea de producción, no clasificación de estado.

**Utilidad.** Potencialmente la más alta de todas por correspondencia con nuestro escenario,
pero **hay que verificar tamaño y licencia antes de considerarlo**.

### 1.4 Dataset for real-time crack detection on chicken eggs (INDIGO / figshare)

| Campo | Valor |
| --- | --- |
| Nombre | Dataset for real-time crack detection on chicken eggs |
| Fuente | INDIGO, University of Illinois at Chicago |
| URL | https://doi.org/10.6084/m9.figshare.21568425.v1 |
| Autores | Botta, Bhavya; Datta, Ashis Kumar |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | 840 (740 de entrenamiento, 100 de prueba) |
| Clases | `egg` y `crack` |
| Formato de anotación | No especificado por la fuente consultada |
| Licencia | No especificado por la fuente consultada (la página exige JavaScript y no se pudo inspeccionar) |
| Publicado | 2022 · 1 cita |

**Ventajas.** Es el único candidato que combina **detección del huevo y detección de la grieta**
como clases separadas, y viene de un repositorio universitario con autoría identificable y DOI,
lo que le da trazabilidad académica. Trae división de entrenamiento y prueba ya hecha.

**Limitaciones.** No se pudo verificar la licencia ni el formato de anotación. Solo cubre
grietas: no hay suciedad ni rotura severa.

**Utilidad.** Alta, y doblemente interesante porque sirve a la vez para la tarea de detección y
para la clase `grieta`. **Requiere verificar la licencia antes de usarlo.**

### 1.5 Candidatos de detección descartados o con reservas serias

| Conjunto | URL | Problema detectado |
| --- | --- | --- |
| egg detection (519 imágenes) | https://universe.roboflow.com/egg-detection-mnb0n/egg-detection-pkaye | La ficha declara **aproximadamente 1.100 clases con nombres numéricos sin significado** (`05517`, `05518`, `05519`…). Un esquema de etiquetas así es inservible para nuestro propósito sin re-etiquetar desde cero. |
| egg (Ultralytics Platform) | https://platform.ultralytics.com/alorrojayann/datasets/egg | 718 imágenes pero **solo 23 etiquetadas y 75 anotaciones**. Está prácticamente sin anotar. Además la descripción indica un único fondo: huevos blancos sobre superficies rojas estampadas, lo que lo hace un candidato claro a sesgo de fondo. |
| Egg Candling V1.0 | https://universe.roboflow.com/eggs-upq8s/egg-candling-v1.0-ns8bl | 1.196 imágenes con división 70/20/10, pero *candling* es **ovoscopía**: inspección del interior del huevo con luz transmitida. Está **explícitamente fuera de nuestro alcance** (ver `01-alcance-del-proyecto.md`, sección 6). |

---

## 2. Conjuntos de datos para el **estado** del huevo

Nuestras clases objetivo son `bueno`, `grieta`, `sucio` y `danado`. **Ningún conjunto encontrado
tiene exactamente esas cuatro clases.** A continuación, lo que hay y cómo se corresponde.

### 2.1 Cracked-Eggs (Roboflow Universe) — dos fichas, posiblemente el mismo material

| Campo | Valor |
| --- | --- |
| Nombre | Cracked-Eggs |
| Fuente | Roboflow Universe |
| URL (A) | https://universe.roboflow.com/eggs-u2ctb/cracked-eggs-gxbbf |
| URL (B) | https://universe.roboflow.com/crackedeggs/cracked-eggs |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | 690 en ambas fichas |
| Clases | `cracked-egg`, `normal-egg` |
| Licencia | CC BY 4.0 (declarada en la ficha B) |
| Publicado | Ficha A: noviembre de 2024 · Ficha B: abril de 2024, 23 descargas |

**Observación importante.** Las dos fichas declaran **exactamente 690 imágenes y exactamente
las mismas dos clases**, con autores distintos. Es muy probable que sea **el mismo conjunto
duplicado o bifurcado**. Si se llegaran a combinar ambos creyendo que son fuentes distintas, se
introducirían duplicados masivos y, con ellos, fuga de información entre particiones. **Hay que
comprobarlo antes de usar cualquiera de los dos.**

**Correspondencia con nuestras clases.** `cracked-egg` → `grieta` (aproximadamente; habría que
ver si incluye roturas severas, que para nosotros serían `danado`). `normal-egg` → `bueno`.
No cubre `sucio`.

### 2.2 Detection Of cracked eggs (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | Detection Of cracked eggs |
| Fuente | Roboflow Universe (autor: EggSorter Pacilan) |
| URL | https://universe.roboflow.com/eggsorter-pacilan/detection-of-cracked-eggs-hse33-dboal |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | Aproximadamente 1.200 |
| Clases | `Brown cracked egg`, `white cracked egg` |
| Licencia | CC BY 4.0 |
| Publicado | Febrero de 2025 · 0 vistas, 0 descargas |

**Limitación grave.** **Las dos clases son huevos agrietados**, diferenciados por color de
cáscara. **No hay clase de huevo sano.** Por sí solo no permite entrenar un clasificador
grieta/bueno: aportaría únicamente ejemplos positivos de grieta. Además el contador de vistas y
descargas en cero sugiere que nadie lo ha revisado.

### 2.3 DIrty Egg (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | DIrty Egg |
| Fuente | Roboflow Universe (autor: geennana) |
| URL | https://universe.roboflow.com/geennana-knbfa/dirty-egg-apelv |
| Tipo de tarea | Clasificación |
| Número de imágenes | 609 |
| Clases | `Dirty-samples` (una sola) |
| Licencia | No especificado por la fuente |
| Publicado | Mayo de 2025 |

**Correspondencia.** `Dirty-samples` → `sucio`. Es el conjunto más grande encontrado para esa
clase concreta. Al tener una sola clase, solo aporta ejemplos positivos de suciedad.

### 2.4 dirt stained egg (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | dirt stained egg |
| Fuente | Roboflow Universe (autor: Anunay Srivastava) |
| URL | https://universe.roboflow.com/anunay-srivastava/dirt-stained-egg |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | 103 |
| Licencia | CC BY 4.0 |
| Publicado | Agosto de 2024 |

**Limitación.** Solo 103 imágenes. Complemento menor para la clase `sucio`.

### 2.5 Egg Quality Grading (Roboflow Universe)

| Campo | Valor |
| --- | --- |
| Nombre | Egg Quality Grading |
| Fuente | Roboflow Universe (autor: VartikaRaj) |
| URL | https://universe.roboflow.com/vartikaraj/egg-quality-grading-wlgy5 |
| Tipo de tarea | Detección de objetos |
| Número de imágenes | Aproximadamente 1.100 |
| Clases declaradas en la descripción | Huevos blancos, marrones, manchados de sangre, manchados de suciedad y con depósitos de calcio |
| Licencia | CC BY 4.0 |
| Publicado | Agosto de 2024 · 17 descargas |

**Ventaja.** Es de los pocos con **descripción escrita por su autor**: declara estar pensado para
granjas avícolas con cámaras de CCTV, lo que se acerca a una línea de clasificación real.

**Desajuste de clases.** Mezcla **color de cáscara** (blanco, marrón) con **defectos**
(manchado de sangre, manchado de suciedad, depósitos de calcio) en un mismo conjunto de
etiquetas. Es el mismo error conceptual que detectamos en nuestra propia clasificación por tipo.
Solo `dirt-stained` se corresponde con una de nuestras clases (`sucio`). "Manchado de sangre" y
"depósitos de calcio" son categorías que nosotros no contemplamos.

### 2.6 Good and Bad Eggs Identification Image Dataset (Mendeley Data)

| Campo | Valor |
| --- | --- |
| Nombre | Good and Bad Eggs Identification Image Dataset |
| Fuente | Mendeley Data |
| URL | https://data.mendeley.com/datasets/mdty358x8m |
| DOI | 10.17632/mdty358x8m.1 |
| Autores | Md Mafiul Hasan Matin, Marium Jahan, Md. Saroar Jahan |
| Tipo de tarea | Clasificación |
| Número de imágenes | 1.000 originales + 6.000 aumentadas |
| Clases | Bueno / malo (binaria) |
| Licencia | **CC BY 4.0** |
| Publicado | 17 de febrero de 2025 |

**Ventajas.** Licencia clara, autoría identificable, DOI citable, imágenes de alta resolución
tomadas en condiciones reales.

**Limitaciones.** Clasificación **binaria**: no distingue entre grieta, suciedad y rotura, que es
precisamente lo que nuestro proyecto necesita. Las 6.000 imágenes aumentadas **no deben contarse
como datos nuevos**: proceden de las 1.000 originales, y mezclarlas entre particiones produciría
fuga de información directa (ver `03-estrategia-dataset.md`, sección 8).

### 2.7 MMU Egg Grading Dataset (Kaggle)

| Campo | Valor |
| --- | --- |
| Nombre | MMU Egg Grading Dataset |
| Fuente | Kaggle (autor: Xin Yao Wong) |
| URL | https://www.kaggle.com/datasets/xinyaowong/mmu-egg-grading-dataset |
| Tipo de tarea | Clasificación y detección |
| Número de imágenes | 3.641 originales, con desbalance de 250 a 930 por clase; 5.580 tras balancear por aumentación |
| Clases | Seis grados de calidad: AA, A, B, C, D, E |
| Formato de anotación | Cajas delimitadoras en formato YOLO, además de las carpetas por clase |
| Resolución | Redimensionado a 224 × 224 px |
| Licencia | Declarada como "Open Database" en la ficha; **el nombre exacto de la licencia no está especificado en la fuente consultada** |

**Ventajas.** Es el conjunto **más grande** encontrado con anotaciones de caja. Su ficha declara
explícitamente variedad de iluminación, fondos y ángulos de visión, que es justo lo que pedimos
en nuestros criterios de captura.

**Limitaciones importantes.** Los grados AA a E son **grados de calidad de una escala concreta**,
no nuestras cuatro clases de estado, y tampoco son los grados de peso de la norma colombiana
(ver sección 3.2). La resolución de 224 × 224 px es baja para detectar una grieta fina. El
balanceo por aumentación vuelve a plantear el problema de la sección 2.6.

### 2.8 Conjuntos de Kaggle con información contradictoria

| Campo | Valor |
| --- | --- |
| Nombre | Eggs image classification: Damaged or not |
| Fuente | Kaggle (autor: abdullahkhanuet22) |
| URL | https://www.kaggle.com/datasets/abdullahkhanuet22/eggs-images-classification-damaged-or-not |
| Licencia | No especificado por la fuente consultada |

**Alerta: las fuentes que lo citan se contradicen.** Al no poder abrir la ficha de Kaggle
directamente, se consultaron trabajos publicados que declaran usar este conjunto, y no coinciden:

- Un artículo en *Journal of Food Science* (DOI 10.1111/1750-3841.17553) declara **794 imágenes
  en dos clases**: dañado e intacto.
- Un artículo indonesio de la revista INTI declara que el mismo conjunto tiene **794 imágenes en
  tres clases**, pero de **tipo** de huevo, no de estado: huevo de gallina *horen* (leghorn),
  de gallina *kampung* (gallina de campo o criolla) y de gallina *árabe*.
- Un artículo en *Academic Research Journal of Technical Vocational Schools* declara que el
  conjunto tiene **7.392 imágenes**, de las cuales seleccionó 472.

**Conclusión.** El contenido real de este conjunto es **incierto**. No debe usarse ninguna de
estas cifras sin abrir la ficha y contar los archivos. El dato interesante, si se confirmara, es
que uno de los trabajos describe clases por **tipo de gallina**, incluida la variedad de campo,
que es el concepto más cercano a "criollo" que se encontró en toda la investigación.

Otro conjunto localizado, **Damaged Eggshells**
(https://www.kaggle.com/datasets/amiski/damaged-eggshells), no pudo consultarse: la página
respondió con una verificación reCAPTCHA. **Todos sus campos quedan como "No especificado por la
fuente".**

### 2.9 Conjuntos descritos en literatura, sin publicación verificada

Estos **no son conjuntos descargables**: son datos privados descritos en artículos. Se incluyen
como referencia metodológica y porque documentan qué taxonomías usa la literatura.

| Trabajo | DOI | Datos descritos | Relevancia para nosotros |
| --- | --- | --- | --- |
| *A novel method for inspection defects in commercial eggs using computer vision* (ISPRS, 2021) | 10.5194/isprs-archives-xliii-b2-2021-809-2021 | 10.000 imágenes de 157 × 252 px: 6.000 normales, 3.500 sucios, 500 agrietados, más 4.000 imágenes vacías. 300 huevos introducidos varias veces en un compartimento cerrado con cadena móvil | **Define operativamente las clases con un umbral explícito**: "normal" admite manchas que no cubran más de 1/32 de la superficie; "sucio" es más de 1/32. Es un criterio objetivo que podríamos adoptar. Su escenario de cadena móvil es muy parecido al nuestro |
| *Egg quality detection based on lightweight HCES-YOLO* (INMATEH) | 10.35633/inmateh-74-43 | 1.100 imágenes, 8 clases: moteado blanco, moteado marrón, cáscara rosada, cáscara blanca, manchado de sangre, cáscara rota, sucio y normal. Ampliadas a 3.300 por aumentación, divididas 7:2:1 | Confirma que en la práctica se mezclan clases de color de cáscara con clases de defecto. Escenario de banda transportadora con bandejas |
| *Attention guided CNN for accurate egg defect detection* (Food and Bioprocess Technology) | 10.1007/s11947-026-04282-5 | 2.400 imágenes, 4 clases: manchado de sangre, agrietado, sucio e intacto. 100 huevos por categoría, 6 ángulos por huevo | **Es la taxonomía publicada más parecida a la nuestra.** Y valida nuestro principio rector: declara explícitamente que "la partición de los datos se realizó a nivel de objeto-huevo y no a nivel de imagen individual", de modo que todas las imágenes de un mismo huevo fueran a la misma partición |
| *Automating egg damage detection…* (Journal of Food Science) | 10.1111/1750-3841.17553 | 794 imágenes, clases dañado e intacto (a partir del conjunto de Kaggle de la sección 2.8) | Referencia de uso del conjunto de Kaggle |

---

## 3. Conjuntos de datos para el **tipo** de huevo

### 3.1 Resultado de la búsqueda: no existe

**No se encontró ningún conjunto de datos público etiquetado como "Triple A", "criollo" o
"semicriollo".** Se buscó en español y en inglés, en Roboflow Universe, Kaggle, Mendeley Data y
repositorios académicos. Los documentos colombianos que describen producción criolla y
semicriolla **no publican conjuntos de imágenes descargables**.

Esto no es un fallo de la búsqueda: es el resultado. Son categorías de un mercado específico y no
existen recursos abiertos etiquetados así.

### 3.2 Qué significa "Triple A": confirmado

La duda que quedó abierta en [`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md),
sección 3b, **queda resuelta**. En Colombia la clasificación de huevo fresco de gallina la
establece la **norma técnica colombiana NTC 1240**, y es una clasificación **por peso**:

| Categoría | Peso |
| --- | --- |
| Jumbo | Más de 78,0 g |
| AAA (Extra grande) | 67,0 – 77,9 g |
| AA (Grande) | 60,0 – 66,9 g |
| A (Mediano) | 53,0 – 59,9 g |
| B (Pequeño) | 46,0 – 52,9 g |
| C | Menos de 46,0 g |

Fuentes consultadas, todas coincidentes en esta tabla:

- CIPA, *Norma ICONTEC para huevos frescos*, tabla de la NTC 1240 vigente desde el 1 de febrero
  de 2012: https://cipa.com.co/wp-content/uploads/2025/02/Normas-icontec-para-huevos-frescos.pdf
- Pronavícola, *Evaluación de la calidad del huevo*, webinar n.º 30:
  https://pronavicola.com/webinar/aspectosevahvo.pdf
- AV Instrumentos, *¿Cómo se realiza el proceso de clasificación de huevos de mesa en Colombia?*:
  https://avinstrumentos.com/blog/avicultura/118-como-se-realiza-el-proceso-de-clasificacion-de-huevos-de-mesa-en-colombia
- Repositorio académico con la tabla atribuida a Fenavi (2012):
  https://hdl.handle.net/20.500.14625/24036

**Advertencia sobre la fuente.** La NTC 1240 es una norma de pago del ICONTEC y **no se consultó
el documento original**. Las cifras provienen de fuentes secundarias que coinciden entre sí. Se
localizó además una versión anterior de la norma con una tabla distinta (categorías Extra, AA, A,
B, C, D con otros rangos de peso), lo que confirma que **la norma ha cambiado con el tiempo** y
que conviene citar siempre la edición. Para el informe final debería consultarse el texto oficial.

**Consecuencia directa para el proyecto:** *Triple A* es una categoría de **peso**, y las tres
categorías del enunciado **no pertenecen al mismo eje de clasificación**. La sospecha registrada
en la auditoría queda confirmada por fuentes.

### 3.3 Qué implica esto para la visión artificial

Una cámara no mide peso. Para que "Triple A" fuera determinable por imagen habría que estimar el
tamaño, y estimar tamaño a partir de una imagen exige una **referencia de escala**. Sin ella, un
huevo pequeño cerca de la cámara produce los mismos píxeles que uno grande lejos.

Existe un precedente publicado que resuelve exactamente ese problema y merece atención (ver 3.4):
fotografiar cada huevo **junto a una moneda de tamaño conocido**.

Aun con una referencia de escala, quedaría un salto que la imagen no puede cubrir sola: el peso
no se deduce del contorno sin asumir una densidad y un modelo de volumen. Lo que se obtendría es
una **estimación**, no la medición que exige la norma.

### 3.4 Lo más cercano encontrado: reconocimiento de variedad de huevo

| Campo | Valor |
| --- | --- |
| Nombre | A Machine-Vision Framework for Automated Egg Variety Recognition, Freshness Assessment, and Nutritional Estimation |
| Fuente | Mendeley Data |
| URL | https://data.mendeley.com/datasets/49msr3ksxj |
| DOI | 10.17632/49msr3ksxj (versión 1: abril de 2026; versión 2: junio de 2026) |
| Autores | Zarif Wasif Bhuiyan, Syed Ali Redwanul Haider |
| Tipo de tarea | Clasificación |
| Número de imágenes | 9.100 imágenes originales (versión 2), más 2.250 imágenes de huevo con moneda |
| Clases | Cinco especies: Bird Koel, **Country Chicken**, Red Layer Chicken, White Layer Chicken, Duck. Además quince clases de especie combinada con frescura (día 0, día 25, día 45) |
| Origen | Mercados locales de Dhaka, Bangladesh, con iluminación práctica |
| Licencia | **No especificado por la fuente consultada** |

**Por qué es el hallazgo más relevante de la sección.** Tres razones:

1. **"Country Chicken" es el concepto análogo a "criollo"**: huevo de gallina de campo frente a
   huevo de gallina ponedora comercial (Red Layer, White Layer). Demuestra que **alguien ya está
   intentando distinguir por imagen RGB lo que nosotros queremos distinguir**, aunque con
   nomenclatura de otro país.
2. **Las 2.250 imágenes de huevo junto a una moneda de 5 taka** son un ejemplo concreto y
   publicado de la referencia de escala que planteamos en la estrategia. Es un patrón que podemos
   imitar en nuestra propia captura.
3. La ficha declara que la aumentación se aplicó **solo al subconjunto de entrenamiento y después
   de dividir**, "para prevenir fuga de información". Es una confirmación externa del principio
   de la sección 8 de nuestra estrategia.

**Limitaciones.** Las variedades son de Bangladesh y **no se corresponden con las colombianas**.
La licencia no está confirmada. Las condiciones de captura (mercado local) no son las de una
banda transportadora.

### 3.5 ¿Son las variedades distinguibles visualmente? Evidencia encontrada

La respuesta corta es que **la literatura considera que el aspecto externo de distintas
variedades es muy parecido**, y por eso recurre a sensores que van más allá de una cámara normal.

Un artículo reciente sobre clasificación de variedades (*Cross-Temporal Egg Variety and Storage
Period Classifications via Multi-Task Deep Learning with Near-Infrared Hyperspectral Imaging*,
https://pmc.ncbi.nlm.nih.gov/articles/PMC12692244/) lo plantea así: *"su aspecto externo similar
los hace vulnerables al etiquetado fraudulento (por ejemplo, huevos corrientes presentados como
variedades premium)"*. Para resolverlo, ese trabajo **no usa una cámara RGB**: usa imagen
hiperespectral en el infrarrojo cercano (1.000 – 2.500 nm), y aun así alcanza alrededor del 86 %
de exactitud sobre tres variedades comerciales.

Otro trabajo con imagen hiperespectral y ELM
(https://www.gpxygpfx.com/EN/abstract/abstract14233.shtml) reporta en torno al 85 % de exactitud
sobre cuatro variedades, también con equipo hiperespectral.

**Interpretación honesta.** Estos resultados no son directamente comparables con nuestro caso:
usan equipos que nosotros no tenemos y variedades distintas. Pero indican con claridad que
**distinguir variedad de huevo es un problema difícil incluso con instrumentación superior a una
webcam**, y que la comunidad científica recurre a información espectral porque el aspecto visible
no basta. Es una señal de advertencia seria para el subpaso 4 de nuestra Fase 1.

Al mismo tiempo, el conjunto de la sección 3.4 muestra que **sí hay quien lo intenta con RGB**.
No podemos concluir que sea imposible; sí podemos concluir que **no debemos darlo por hecho**.

---

## 4. Compatibilidad entre conjuntos de datos

### 4.1 Comparación de los candidatos

| Conjunto | Tarea | Cajas | Clases | Resolución | Fondo / escenario | Licencia |
| --- | --- | --- | --- | --- | --- | --- |
| Egg-Detection (HF) | Detección | Sí | 2 (color) | No especificado | Bandejas y cajas variadas | MIT |
| egg detection final | Detección | Sí | No especificado | No especificado | No especificado | CC BY 4.0 |
| Egg-count-detection-1 | Detección | Sí | 1 (`Egg`) | No especificado | Banda transportadora (declarado) | No especificado |
| Crack detection (INDIGO) | Detección | Sí | 2 (`egg`, `crack`) | No especificado | No especificado | No especificado |
| Cracked-Eggs | Detección | Sí | 2 (estado) | No especificado | No especificado | CC BY 4.0 |
| Detection Of cracked eggs | Detección | Sí | 2 (ambas agrietadas) | No especificado | No especificado | CC BY 4.0 |
| DIrty Egg | Clasificación | No | 1 (`sucio`) | No especificado | No especificado | No especificado |
| dirt stained egg | Detección | Sí | 1 | No especificado | No especificado | CC BY 4.0 |
| Egg Quality Grading | Detección | Sí | 5 (mezcladas) | No especificado | CCTV en granja (declarado) | CC BY 4.0 |
| Good and Bad Eggs | Clasificación | No | 2 (binaria) | Alta (declarada) | Condiciones reales | CC BY 4.0 |
| MMU Egg Grading | Ambas | Sí (YOLO) | 6 (grados) | 224 × 224 | Variado (declarado) | "Open Database" |
| Egg Variety (Mendeley) | Clasificación | No | 5 especies + 15 frescura | Alta (declarada) | Mercado local | No especificado |

### 4.2 Problemas de compatibilidad detectados

**Desplazamiento de dominio (*domain shift*).** Es el riesgo principal. Los candidatos provienen
de escenarios muy distintos: bandejas de cartón, cintas industriales con CCTV, mercados de
Dhaka, superficies rojas estampadas. Nuestro escenario será una banda simulada, montada por
nosotros, con nuestra iluminación. Un modelo entrenado mayoritariamente con material público
puede funcionar bien en validación y fallar frente a nuestra cámara. **Mitigación:** reservar una
partición de prueba compuesta exclusivamente por imágenes propias, además de la partición mixta.

**Clases incompatibles.** Ningún conjunto usa nuestras cuatro clases. Los desajustes concretos:

| Nuestra clase | Qué ofrece el material público | Desajuste |
| --- | --- | --- |
| `bueno` | `normal-egg`, "intacto", "bueno" | Aceptable, pero cada fuente define "normal" con un criterio distinto |
| `grieta` | `cracked-egg`, `crack` | Aceptable. Hay que verificar si incluye roturas severas que para nosotros serían `danado` |
| `sucio` | `Dirty-samples`, `dirt-stained` | Aceptable, pero sin umbral común. El trabajo de ISPRS usa 1/32 de la superficie; los conjuntos de Roboflow no declaran umbral |
| `danado` | **Casi nada** | Es nuestra clase peor cubierta. "Broken shell" aparece en conjuntos privados de la literatura, no en los públicos descargables |

Además varios conjuntos introducen clases que no queremos (manchado de sangre, depósitos de
calcio, moteado) y clases de **color de cáscara** mezcladas con clases de **defecto**, lo que
obligaría a remapear etiquetas antes de combinar.

**Imágenes duplicadas.** Riesgo confirmado en dos frentes: las dos fichas de Cracked-Eggs con
690 imágenes idénticas en número y clases (sección 2.1), y las versiones aumentadas de Good and
Bad Eggs y MMU Egg Grading, donde miles de imágenes derivan de unos cientos de originales.
**Combinar sin deduplicar produciría fuga de información garantizada.**

**Fondos demasiado homogéneos.** El conjunto de Ultralytics es el caso extremo: un único tipo de
fondo (superficies rojas estampadas). Varios conjuntos de Roboflow no describen sus condiciones,
así que el riesgo no puede descartarse sin mirar las imágenes.

**Sesgo del conjunto de datos.** Tres sesgos identificables. Uno **geográfico y de raza**: el
material disponible refleja las razas y prácticas comerciales de sus países de origen, ninguno
colombiano. Uno **de balance**: donde se publican conteos, las clases de defecto son muy
minoritarias (en el trabajo de ISPRS, 500 agrietados frente a 6.000 normales). Y uno **de
resolución**: 224 × 224 px puede bastar para ver suciedad, pero es dudoso para una fisura fina.

**Resoluciones dispares.** Van desde 157 × 252 px en la literatura hasta "alta resolución" sin
especificar. Homogeneizar hacia abajo destruiría el detalle necesario para detectar grietas.

---

## 5. Conjuntos de datos candidatos

Recomendación basada **exclusivamente** en la información encontrada y recogida arriba. Nada de
esto se ha descargado ni verificado imagen por imagen.

### A. Detección de huevos

**Mejor candidato: Egg-Detection de Hugging Face** (https://huggingface.co/datasets/afshin-dini/Egg-Detection).
Es el único con licencia permisiva confirmada en su propia ficha (MIT), viene en formato YOLO
listo para usar, tiene código de referencia asociado y su autor buscó deliberadamente variedad de
fondos. Sus dos clases se fusionan sin problema en nuestra clase única `egg`.

**Alternativa: Egg-count-detection-1 de Roboflow**
(https://universe.roboflow.com/data-science-devhu/egg-count-detection-1), por ser el único cuyo
escenario declarado es una banda transportadora y por usar ya una sola clase `Egg`. **Condicionado
a verificar número de imágenes y licencia**, que su ficha no publica. Como segunda alternativa,
*egg detection final* (https://universe.roboflow.com/egg-detection-mnb0n/egg-detection-final),
con licencia CC BY 4.0 confirmada pero sin descripción de contenido.

**¿Hacen falta datos propios?** Para la detección, **probablemente no como base, pero sí como
complemento**. Entre los candidatos hay material suficiente para entrenar un detector de una
clase. Lo que ninguno aporta es nuestro escenario concreto, así que harán falta imágenes propias
para ajuste final y, sobre todo, para una partición de prueba honesta.

### B. Clasificación del estado

**Mejor candidato: no hay uno solo. Hay que combinar.** La combinación mínima que cubre tres de
nuestras cuatro clases sería:

| Clase | Fuente propuesta |
| --- | --- |
| `grieta` | Crack detection de INDIGO (840 imágenes, clases `egg` y `crack`), verificando licencia, más Cracked-Eggs de Roboflow |
| `bueno` | `normal-egg` de Cracked-Eggs; Good and Bad Eggs de Mendeley, usando **solo las 1.000 originales** |
| `sucio` | DIrty Egg (609 imágenes) y dirt stained egg (103 imágenes) |
| `danado` | **Sin fuente pública adecuada** |

**Alternativa: MMU Egg Grading** (https://www.kaggle.com/datasets/xinyaowong/mmu-egg-grading-dataset),
que es el único conjunto grande con anotaciones YOLO y variedad declarada de iluminación y
fondos. Pero su esquema de seis grados **no se corresponde con nuestras clases** y habría que
inspeccionarlo para ver si sus grados se pueden remapear. Su resolución de 224 × 224 px es una
reserva seria para detectar grietas.

**¿Hacen falta datos propios? Sí, con seguridad.** Por tres razones: la clase `danado` no tiene
cobertura pública; no existe ningún conjunto con las cuatro clases juntas, de modo que combinar
fuentes con criterios de etiquetado distintos degradaría la consistencia; y ninguna fuente usa
nuestro escenario.

### C. Clasificación del tipo

**Mejor candidato: no existe.** No hay ningún conjunto público etiquetado como Triple A, criollo
o semicriollo.

**Alternativa parcial: el conjunto de variedades de Mendeley**
(https://data.mendeley.com/datasets/49msr3ksxj), únicamente como **referencia metodológica**: su
clase "Country Chicken" es el análogo conceptual de "criollo" y sus 2.250 imágenes con moneda de
referencia muestran cómo montar la escala. Sus variedades no son las colombianas y su licencia no
está confirmada, así que **no sirve como fuente de entrenamiento para nuestras categorías**.

**¿Hacen falta datos propios? Sí, y es la única vía.** Con dos advertencias que deben pesar en la
decisión: primero, "Triple A" es una categoría de **peso** según la NTC 1240, de modo que
etiquetar por tipo exigiría **pesar cada huevo** en el momento de la captura para tener una
etiqueta verdadera; segundo, la literatura sugiere que distinguir variedades por aspecto externo
es difícil incluso con imagen hiperespectral.

---

## 6. Resultado de esta investigación

### 6.1 Qué parece útil

1. **Egg-Detection de Hugging Face**, licencia MIT, formato YOLO: el candidato más sólido de
   toda la investigación y la base propuesta para el detector.
2. **Crack detection de INDIGO** (840 imágenes, clases `egg` y `crack`): sirve a la vez para
   detección y para la clase `grieta`, con respaldo universitario y DOI. Sujeto a verificar
   licencia.
3. **Cracked-Eggs de Roboflow** (690 imágenes, CC BY 4.0) para `grieta` y `bueno`, tras
   comprobar si las dos fichas son el mismo material.
4. **DIrty Egg** (609 imágenes) y **dirt stained egg** (103 imágenes) para `sucio`.
5. **Good and Bad Eggs de Mendeley** (1.000 originales, CC BY 4.0) como refuerzo binario.
6. **Egg-count-detection-1**, por su escenario de banda, si se confirman tamaño y licencia.

### 6.2 Qué no sirve

1. **egg detection (519 imágenes) de Roboflow**: unas 1.100 clases con nombres numéricos sin
   significado.
2. **Egg (Ultralytics)**: 718 imágenes con solo 23 etiquetadas, y un único tipo de fondo.
3. **Egg Candling V1.0**: es ovoscopía, explícitamente fuera de nuestro alcance.
4. **Detection Of cracked eggs**: sus dos clases son huevos agrietados; sin clase de huevo sano
   no sirve por sí solo.
5. **Damaged Eggshells de Kaggle**: no se pudo consultar; sin datos no es evaluable.
6. **Eggs image classification: Damaged or not**: tres fuentes publicadas se contradicen sobre su
   contenido; inutilizable hasta verificarlo directamente.

### 6.3 Qué clases faltan

| Clase | Cobertura pública |
| --- | --- |
| `bueno` | Suficiente, aunque con definiciones heterogéneas entre fuentes |
| `grieta` | Suficiente |
| `sucio` | Escasa pero existente (unas 700 imágenes sumando dos fuentes) |
| `danado` | **Prácticamente nula.** Solo aparece como "broken shell" en conjuntos privados descritos en artículos |
| Triple A / criollo / semicriollo | **Inexistente** |

### 6.4 Qué deberíamos capturar nosotros

1. **Huevos dañados** (rotura importante, deformación): la clase sin cobertura pública.
2. **Imágenes en nuestro escenario de banda simulada**, con nuestra cámara, nuestra iluminación y
   nuestro fondo, como mínimo para construir una partición de prueba honesta.
3. **Todas las categorías de tipo**, si se mantiene ese requisito: no hay alternativa pública.
4. **Registro de peso por huevo**, si "Triple A" se conserva como categoría. Sin báscula no hay
   etiqueta verdadera posible para una categoría definida por peso.
5. **Una referencia de escala en la escena**, siguiendo el patrón de la moneda del conjunto de
   Mendeley, si se pretende estimar calibre.

### 6.5 Incertidumbres que siguen abiertas

1. **Licencias sin confirmar** en cuatro candidatos: Crack detection de INDIGO,
   Egg-count-detection-1, DIrty Egg y el conjunto de variedades de Mendeley. Dos de ellos están
   entre los mejores.
2. **Contenido real sin verificar** de todo el material de Roboflow y Kaggle: sus fichas no se
   pudieron abrir directamente y no se ha visto ninguna imagen.
3. **Duplicación entre las dos fichas de Cracked-Eggs**: sin resolver.
4. **Correspondencia de clases**: no se sabe si `cracked-egg` incluye roturas que nosotros
   llamaríamos `danado`, ni con qué umbral etiqueta cada fuente la suciedad.
5. **Viabilidad de la clasificación por tipo**: sigue abierta. Hay evidencia de que es difícil por
   aspecto externo, y evidencia de que alguien lo intenta con RGB. No se puede decidir sin datos.
6. **Definición de "criollo" y "semicriollo"**: no se encontró una definición normativa
   colombiana equivalente a la que sí existe para el calibre. Falta esa fuente.
7. **Texto oficial de la NTC 1240**: es una norma de pago y no se consultó el original. Las cifras
   provienen de fuentes secundarias coincidentes.

### 6.6 Estado tras este subpaso

- **No se ha descargado ningún conjunto de datos.**
- **No se ha capturado ninguna imagen.**
- **No se ha entrenado ningún modelo.**
- **No se ha inspeccionado ninguna imagen de ningún conjunto.**
- Queda **confirmado por fuentes** que "Triple A" es una categoría de peso de la NTC 1240 y que,
  por tanto, las tres categorías de tipo del enunciado no pertenecen al mismo eje. Esto cierra la
  pregunta 2 de la sección 1.3 de [`03-estrategia-dataset.md`](03-estrategia-dataset.md).

**Siguiente paso (subpaso 3 de la Fase 1):** validar las categorías de clasificación. Con la
confirmación sobre el calibre ya disponible, la decisión pendiente es qué hacer con el requisito
de tipo: separarlo en atributos independientes, redefinirlo sin depender del peso, o acotarlo
fuera del alcance con la justificación documentada.
