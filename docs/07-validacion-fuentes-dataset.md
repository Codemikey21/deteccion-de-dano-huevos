# Validación de fuentes y plan de descarga

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase 1, subpaso 6: validar las fuentes antes de descargar
Documentos relacionados: [`04-investigacion-datasets.md`](04-investigacion-datasets.md) ·
[`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md)

> **No se ha descargado ningún conjunto de datos.** Este documento resuelve las verificaciones
> pendientes listadas en [`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md), sección 7.
> Solo se consultaron **metadatos** (APIs públicas de catálogo y fichas web). No se descargó
> ningún archivo de imágenes, no se crearon credenciales y `data/` sigue vacío.

---

## 0. Método de verificación

Las fichas de Roboflow Universe **no se pudieron abrir** en la investigación previa por la
protección anti-bot de Cloudflare. Para esta validación se intentó una vía distinta: consultar
las **APIs públicas de metadatos** de cada plataforma, que devuelven la licencia declarada de
forma estructurada y citable.

| Plataforma | Vía usada | Resultado |
| --- | --- | --- |
| Hugging Face | `https://huggingface.co/api/datasets/{id}` | **Funcionó** |
| figshare | `https://api.figshare.com/v2/articles/{id}` | **Funcionó** |
| Mendeley Data | DataCite: `https://api.datacite.org/dois/{doi}` | **Funcionó** |
| Kaggle | Ficha web pública | **Funcionó** |
| Roboflow Universe | Ficha web pública | **Bloqueado por Cloudflare** (verificación de seguridad) |

Fecha de la consulta: **21 de septiembre de 2026**.

Consecuencia directa: **todo lo alojado en Roboflow Universe queda sin verificar**, y todo lo
alojado en repositorios académicos o en Hugging Face quedó verificado. Esto no es casualidad:
los repositorios con DOI publican su licencia como metadato estructurado precisamente para que
pueda citarse.

---

## 1. Validación de licencias

### 1.1 APROBADO PARA USO

#### Egg-Detection — Hugging Face

| Campo | Valor |
| --- | --- |
| URL | https://huggingface.co/datasets/afshin-dini/Egg-Detection |
| **Licencia** | **MIT** |
| Fuente de la verificación | API de Hugging Face, campo `cardData.license` = `mit`; etiqueta `license:mit` |
| Datos confirmados en la misma consulta | Autor `afshin-dini`; 322 descargas en el último mes; categoría de tamaño `n<1K`; última modificación 18/03/2025 |
| Contenido auditado (árbol de archivos, 21/09/2026, sin descargar) | **51 imágenes** (49 `train`, 2 `val`), **423 cajas anotadas**, 108 archivos, 339,47 MiB ≈ 355,96 MB |
| Obligaciones | Atribución y conservación del aviso de licencia |

> **La partición original no sirve para una validación seria.** Dos imágenes en `val` no permiten
> medir nada con sentido. Al preparar el conjunto se rehará la división en `train` / `validation`
> / `test`. No se crea ninguna partición todavía.

#### Dataset for real-time crack detection on chicken eggs — figshare (INDIGO)

| Campo | Valor |
| --- | --- |
| URL | https://doi.org/10.6084/m9.figshare.21568425.v1 |
| **Licencia** | **CC BY 4.0** |
| Fuente de la verificación | API de figshare, `license.name` = `CC BY 4.0`, `license.url` = `https://creativecommons.org/licenses/by/4.0/` |
| Datos confirmados en la misma consulta | Autores: Bhavya Botta y Ashis Kumar Datta. Publicado 16/11/2022. `is_public` = verdadero. **840 imágenes (740 de entrenamiento, 100 de prueba)** confirmadas en la descripción oficial. Clases `egg` y `crack` |
| Tamaño real | `train.zip` 1,95 GB + `test.zip` 267 MB ≈ **2,5 GB** |
| Obligaciones | Atribución con cita del DOI y los autores |

**Esta era la incógnita bloqueante más importante del documento anterior, y queda resuelta en
favorable.** El conjunto es reutilizable con atribución.

**Nota operativa:** la lista de archivos del registro muestra `test.zip` **dos veces**, con un
tamaño idéntico de 266.920.567 bytes. Casi con certeza es la misma entrada repetida en los
metadatos, pero conviene comprobarlo al descargar para no duplicar la partición de prueba.

**Nota de tamaño:** 2,5 GB es el conjunto más pesado de la selección. Debe descargarse a
`data/raw/public/`, que está excluido del control de versiones, y no acercarse nunca al
repositorio.

#### Good and Bad Eggs Identification Image Dataset — Mendeley Data

| Campo | Valor |
| --- | --- |
| URL | https://data.mendeley.com/datasets/mdty358x8m/1 |
| DOI | 10.17632/mdty358x8m.1 |
| **Licencia** | **CC BY 4.0** |
| Fuente de la verificación | API de DataCite, `rightsList`: `rightsIdentifier` = `cc-by-4.0`, esquema SPDX, más `info:eu-repo/semantics/openAccess` |
| Datos confirmados | Autores: Md Mafiul Hasan Matin, Marium Jahan, Md. Saroar Jahan. Publicado 17/02/2025. **1.000 imágenes originales + 6.000 aumentadas** confirmadas en la descripción oficial |
| Obligaciones | Atribución con cita del DOI y los autores |

### 1.2 APROBADO CON RESERVA DE LICENCIA

#### MMU Egg Grading Dataset — Kaggle

| Campo | Valor |
| --- | --- |
| URL | https://www.kaggle.com/datasets/xinyaowong/mmu-egg-grading-dataset |
| **Licencia** | **"Database: Open Database, Contents: Database Contents"** |
| Fuente de la verificación | Ficha pública de Kaggle, sección License |
| Interpretación | Corresponde a **ODbL** para la base de datos y **DbCL** para los contenidos |
| Datos confirmados | 3.641 originales con desbalance de 250 a 930 por clase; 5.580 tras balancear; **224 × 224 px**; anotaciones en formato YOLO; 16,7 mil archivos en **39,47 MB**; declarado "Self-Collected"; 69 descargas y 737 visitas históricas |

**La licencia sí está identificada, pero introduce una obligación distinta a las demás: ODbL es
una licencia con cláusula de tipo *share-alike*.** Si se construyera una base de datos derivada y
se publicara, habría que publicarla bajo la misma licencia. Para un trabajo académico es
manejable, pero no es equivalente a MIT ni a CC BY.

**Se mantiene como reserva y no se descarga**, por el motivo ya expuesto en
[`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md): sus seis grados AA–E son una escala
ajena que no se corresponde con nuestras cuatro clases. Y el dato de 39,47 MB para 16,7 mil
archivos **confirma por aritmética** que las imágenes son diminutas, coherente con los 224 × 224
px declarados: insuficiente para distinguir una fisura fina.

### 1.3 PENDIENTE — LICENCIA NO VERIFICADA

Todos los conjuntos alojados en **Roboflow Universe**. El acceso a sus fichas está bloqueado por
Cloudflare, tanto por navegación directa como por las vías alternativas intentadas.

| Conjunto | Licencia declarada en resultados de búsqueda | Estado real |
| --- | --- | --- |
| Cracked-Eggs (ficha B) | CC BY 4.0 | **LICENCIA NO VERIFICADA** |
| Cracked-Eggs (ficha A) | No especificado | **LICENCIA NO VERIFICADA** |
| Detection Of cracked eggs | CC BY 4.0 | **LICENCIA NO VERIFICADA** |
| DIrty Egg | No especificado | **LICENCIA NO VERIFICADA** |
| dirt stained egg | CC BY 4.0 | **LICENCIA NO VERIFICADA** |
| Egg Quality Grading | CC BY 4.0 | **LICENCIA NO VERIFICADA** |
| egg detection final | CC BY 4.0 | **LICENCIA NO VERIFICADA** |
| Egg-count-detection-1 | No especificado | **LICENCIA NO VERIFICADA** |

**Por qué no basta el dato del buscador.** Las menciones de "CC BY 4.0" provienen de fragmentos
indexados por motores de búsqueda, no de la ficha leída directamente. Un fragmento indexado puede
estar desactualizado, puede corresponder a otra versión del conjunto o puede ser una plantilla
genérica del sitio. Para un documento académico que declara procedencias, **eso no es una fuente
verificable**, y el enunciado de este subpaso pide explícitamente no asumir que un conjunto
público puede redistribuirse libremente.

**Vía de resolución**: abrir cada ficha manualmente en un navegador, con sesión iniciada si hace
falta, y registrar en este documento la licencia mostrada junto con la fecha de consulta. Es un
trámite de minutos, pero requiere intervención humana porque la protección anti-bot está
precisamente diseñada para impedir que lo haga un proceso automatizado.

### 1.4 DESCARTADO

| Conjunto | Motivo |
| --- | --- |
| Eggs image classification: Damaged or not (Kaggle) | Tres publicaciones que dicen usarlo se contradicen sobre su contenido: 794 imágenes en dos clases de daño, 794 en tres clases de tipo de gallina, y 7.392 imágenes. Contenido indeterminado |
| egg detection (519 imágenes, Roboflow) | Aproximadamente 1.100 clases con nombres numéricos sin significado |
| egg (Ultralytics Platform) | Solo 23 imágenes etiquetadas de 718; fondo único, candidato claro a sesgo |
| Egg Candling V1.0 | Ovoscopía, inspección interna por transiluminación: fuera del alcance del proyecto |

---

## 2. Validación de duplicados entre fuentes

### 2.1 Cracked-Eggs: dos fichas, sospecha fuerte, no demostrada

| Ficha | URL | Imágenes | Clases |
| --- | --- | --- | --- |
| A | https://universe.roboflow.com/eggs-u2ctb/cracked-eggs-gxbbf | 690 | `cracked-egg`, `normal-egg` |
| B | https://universe.roboflow.com/crackedeggs/cracked-eggs | 690 | `cracked-egg`, `normal-egg` |

**Indicios de que son el mismo material**: número de imágenes idéntico al entero, conjunto de
clases idéntico incluida la forma exacta de escribirlas, y el mismo nombre de proyecto.

**Por qué no se afirma**: no se han podido abrir las fichas ni ver una sola imagen. Una
coincidencia de 690 imágenes y dos clases idénticas es un indicio fuerte, pero no una
demostración. Podría tratarse de dos equipos que partieron del mismo material de origen y
anotaron por separado, o de una bifurcación legítima con anotaciones distintas.

**Estado: SOSPECHA FUERTE, NO DEMOSTRADA.**

**Regla de seguridad mientras no se demuestre**: usar **una sola de las dos fichas**. Si resultan
ser copias y se usaran ambas, cada imagen entraría dos veces en el conjunto, y bastaría con que
una copia cayera en entrenamiento y otra en prueba para que el modelo fuera evaluado sobre
imágenes que ya vio. La métrica resultante sería falsamente buena. El coste de equivocarse por
prudencia es no usar 690 imágenes; el coste de equivocarse por confianza es invalidar la
evaluación.

### 2.2 Duplicado demostrado dentro del registro de INDIGO

La lista de archivos devuelta por la API de figshare contiene **`test.zip` repetido**, con el
mismo tamaño exacto en bytes. Es el único caso de duplicación que puede demostrarse con una
fuente consultable, aunque es casi seguro que se trata de una repetición en los metadatos y no de
dos archivos distintos. Se comprobará al descargar.

### 2.3 Replicación entre plataformas

No se encontró evidencia de que ninguno de los conjuntos aprobados esté republicado en otra
plataforma bajo otro nombre:

- **Egg-Detection (Hugging Face)** tiene autoría y repositorio de código propios.
- **INDIGO** tiene DOI y publicación académica asociada.
- **Good and Bad Eggs (Mendeley)** tiene DOI y tres autores identificados.
- **MMU Egg Grading** se declara explícitamente "Self-Collected" en su ficha.

**No puede descartarse** la replicación entre los conjuntos de grietas de Roboflow y el de
INDIGO, porque los de Roboflow no son inspeccionables. Si finalmente se usaran ambos, habría que
buscar duplicados por comparación de imágenes antes de dividir en particiones.

---

## 3. Validación de etiquetas

Ninguna equivalencia puede marcarse como **VALIDADA**, por una razón simple: **no se ha
inspeccionado todavía ninguna imagen**. La validación completa exige ver el material. Lo que sí
puede hacerse ahora es distinguir las equivalencias razonablemente sostenidas por la documentación
oficial de la fuente, de las que descansan únicamente en el nombre de la etiqueta.

### 3.1 Detección

```
clases originales  ->  egg              (Egg-Detection, Hugging Face)
Estado: PENDIENTE DE VERIFICACIÓN
Motivo: la ficha sugiere dos clases por color de cáscara, y en el plano conceptual
        ambas designarían huevos, fusionables en nuestra clase única `egg`.
        Los nombres exactos y su orden numérico están en `data/data.yaml`, que
        todavía no se ha leído. Hasta entonces no se afirma que las clases sean
        `white-egg` y `brown-egg`.

egg  ->  egg                            (INDIGO, figshare)
Estado: PARCIALMENTE VALIDADO
Motivo: la descripción oficial del registro dice literalmente "annotations for egg
        and crack classes", de modo que el significado de la etiqueta está respaldado
        por la fuente y no solo por su nombre. Falta ver las cajas.
```

### 3.2 Estado visual

```
crack  ->  grieta                       (INDIGO, figshare)
Estado: PARCIALMENTE VALIDADO
Motivo: que la etiqueta designa una fisura está respaldado por la descripción oficial
        y por la publicación asociada. Lo que NO está resuelto es la frontera con
        nuestra clase `danado`: una etiqueta `crack` unica probablemente incluye desde
        fisuras finas hasta roturas severas, y nuestra taxonomia las separa. Requiere
        inspeccion visual para decidir si se separan manualmente los casos severos.

good  ->  bueno                         (Good and Bad Eggs, Mendeley)
Estado: NO VALIDADO
Motivo: es una clasificacion binaria bueno/malo. Nuestra clase `bueno` exige DOS
        condiciones, integridad y ausencia de suciedad, mientras que la suya exige
        solo la negacion de "malo". Ademas su descripcion oficial dice que el conjunto
        captura "shell texture, color, shape, and visible defects", lo que sugiere que
        la clase "malo" mezcla varios defectos distintos sin separarlos. Un huevo
        intacto pero sucio podria estar en cualquiera de las dos clases.

bad  ->  (sin destino)                  (Good and Bad Eggs, Mendeley)
Estado: NO VALIDADO, SIN DESTINO ASIGNABLE
Motivo: "malo" es un agregado que puede contener grietas, suciedad, roturas y
        deformaciones a la vez. No puede remapearse a ninguna de nuestras cuatro
        clases sin separarlo antes a mano. Es material potencialmente util, pero
        exige reetiquetado, no remapeo.

normal-egg  ->  bueno                   (Cracked-Eggs, Roboflow)
cracked-egg ->  grieta                  (Cracked-Eggs, Roboflow)
Dirty-samples -> sucio                  (DIrty Egg, Roboflow)
dirt-stained  -> sucio                  (Egg Quality Grading, Roboflow)
Estado: NO VALIDADO, Y ADEMAS BLOQUEADO POR LICENCIA
Motivo: ninguna de estas fichas es accesible, de modo que no hay documentacion oficial
        que respalde el significado de las etiquetas, solo su nombre. En el caso de
        `normal-egg` el problema es el mismo que con "good": "normal" significa "no
        agrietado", no significa "limpio". En el caso de las etiquetas de suciedad,
        ninguna fuente declara un umbral de cuanta suciedad hace que un huevo sea
        sucio.
```

### 3.3 Resumen

| Equivalencia | Estado | Bloqueada por licencia |
| --- | --- | --- |
| clases de Egg-Detection → `egg` | **PENDIENTE DE VERIFICACIÓN** (nombres en `data.yaml` no leídos) | No |
| `egg` → `egg` | PARCIALMENTE VALIDADO | No |
| `crack` → `grieta` | PARCIALMENTE VALIDADO | No |
| `good` → `bueno` | NO VALIDADO | No |
| `bad` → sin destino | NO VALIDADO | No |
| `normal-egg` → `bueno` | NO VALIDADO | **Sí** |
| `cracked-egg` → `grieta` | NO VALIDADO | **Sí** |
| `Dirty-samples` → `sucio` | NO VALIDADO | **Sí** |
| `dirt-stained` → `sucio` | NO VALIDADO | **Sí** |

---

## 4. Plan de descarga

| Dataset | Uso | Estado | ¿Descargar ahora? | Motivo |
| --- | --- | --- | --- | --- |
| Egg-Detection (Hugging Face) | Detección `egg` | Licencia MIT verificada | **SÍ** | Licencia confirmada por API, formato YOLO, equivalencia de etiquetas sólida |
| Crack detection (INDIGO, figshare) | Detección `egg` + estado `grieta` | Licencia CC BY 4.0 verificada | **SÍ** | Licencia confirmada por API. Aporta a las dos tareas. Atención: 2,5 GB |
| Good and Bad Eggs (Mendeley) | Estado, candidato a `bueno` | Licencia CC BY 4.0 verificada | **SÍ, solo las 1.000 originales** | Licencia confirmada por DataCite. Se descarga **para inspeccionar** las clases, no para usarlas directamente. Las 6.000 aumentadas se excluyen |
| MMU Egg Grading (Kaggle) | Reserva | Licencia ODbL/DbCL identificada | **NO** | La licencia ya no es el problema; lo es que sus grados AA–E no corresponden a nuestras clases y que 224 × 224 px es poco para una fisura |
| Cracked-Eggs (Roboflow) | Estado `grieta` y `bueno` | **Licencia no verificada** + posible duplicado | **NO** | Dos bloqueos simultáneos sin resolver |
| Detection Of cracked eggs (Roboflow) | Estado `grieta` | **Licencia no verificada** | **NO** | Licencia sin confirmar; además carece de huevos sanos |
| DIrty Egg (Roboflow) | Estado `sucio` | **Licencia no verificada** | **NO** | Licencia sin confirmar |
| dirt stained egg (Roboflow) | Estado `sucio` | **Licencia no verificada** | **NO** | Licencia sin confirmar |
| Egg Quality Grading (Roboflow) | Estado `sucio` parcial | **Licencia no verificada** | **NO** | Licencia sin confirmar; además mezcla ejes de clasificación |
| egg detection final (Roboflow) | Detección | **Licencia no verificada** + clases desconocidas | **NO** | Dos datos esenciales sin confirmar |
| Egg-count-detection-1 (Roboflow) | Detección en banda | **Licencia no verificada** + tamaño desconocido | **NO** | Es el de escenario más parecido al nuestro, y por eso conviene resolverlo, pero no puede descargarse a ciegas |
| Eggs image classification: Damaged or not | — | Descartado | **NO** | Contenido contradictorio entre fuentes |

### 4.1 Consecuencia de la validación sobre la cobertura de clases

La verificación de licencias **cambia el panorama respecto a
[`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md)**, y no de forma menor:

| Clase | Cobertura antes de validar | Cobertura con licencia verificada |
| --- | --- | --- |
| `egg` (detección) | 1 fuente aprobada | **2 fuentes aprobadas**, 891 imágenes (51 + 840) |
| `grieta` | 3 fuentes, ninguna confirmada | **1 fuente aprobada** (INDIGO) |
| `bueno` | 2 fuentes | **1 fuente aprobada, y con etiqueta no validada** |
| `sucio` | 3 fuentes | **Ninguna fuente aprobada** |
| `danado` | Ninguna | **Ninguna** |

> **Corrección de cifras (21/09/2026).** Una versión anterior de esta tabla decía
> «aproximadamente 1.260 imágenes», sumando las 423 atribuidas entonces a Egg-Detection más las
> 840 de INDIGO. **Egg-Detection tiene 51 imágenes, no 423**: esa cifra era su número de cajas
> anotadas. La suma correcta es **51 + 840 = 891 imágenes**. Las 51 imágenes de Egg-Detection
> contienen **423 cajas anotadas**, de modo que en número de objetos su aportación es mayor de lo
> que sugiere el recuento de imágenes. Ver la comprobación en
> [`04-investigacion-datasets.md`](04-investigacion-datasets.md), sección 1.1.

Dicho de forma directa: **las tres fuentes de `sucio` estaban todas en Roboflow**, así que al
exigir licencia verificada esa clase se queda sin cobertura pública alguna. **Dos de las cuatro
clases del MVP, `sucio` y `danado`, no tienen hoy ninguna fuente pública utilizable.**

Esto no obliga a cambiar el MVP. Obliga a reconocer que **la captura propia pasa de ser un
complemento a ser la fuente principal del clasificador de estado**, y que el material público
aprobado sirve sobre todo para la detección, que es donde sí hay cobertura sólida.

### 4.2 Obligaciones de atribución

Los tres conjuntos aprobados exigen atribución: MIT en uno y CC BY 4.0 en dos. Antes de usarlos
habrá que registrar en el repositorio, por cada conjunto, el nombre, los autores, la URL o el
DOI, la licencia y la fecha de consulta. **Ese archivo no se crea en este subpaso**, pero la
obligación queda anotada para no descubrirla al final.

---

## 5. Plan de datos propios

### 5.1 Qué se capturará

Imágenes propias de las **cuatro clases** del MVP: `bueno`, `grieta`, `sucio` y `danado`.

No solo de `danado`, aunque sea la única sin ninguna alternativa. Las cuatro.

### 5.2 Por qué las cuatro, y no solo las que faltan

Porque si cada clase proviene de una fuente distinta, **el modelo puede resolver el problema sin
mirar el huevo**.

El razonamiento, que ya se anticipó en
[`06-seleccion-dataset-mvp.md`](06-seleccion-dataset-mvp.md) sección 5.2, es el siguiente. Cada
conjunto de datos tiene su propia cámara, su propia iluminación, su propio fondo y su propia
resolución. Si todos los `bueno` vienen de un conjunto y todos los `grieta` de otro, entonces el
aspecto general de la imagen —el tono, el grano, el fondo— **predice la etiqueta perfectamente**.
Una red aprende ese atajo antes que a reconocer una fisura, porque es una señal mucho más fácil.

El resultado sería un modelo con métricas excelentes en prueba y comportamiento errático en la
banda real. Allí las cuatro clases llegan con la misma cámara, la misma luz y el mismo fondo, así
que el atajo desaparece y el modelo se queda sin aquello en lo que realmente se apoyaba.

La defensa es capturar las cuatro clases **en condiciones idénticas**, de modo que las condiciones
de captura no aporten ninguna información sobre la clase. Si el fondo es el mismo para un huevo
bueno y uno agrietado, el fondo deja de ser una pista y el modelo se ve obligado a mirar la
cáscara.

### 5.3 Condiciones de captura

La regla que gobierna todo lo que sigue: **ninguna condición de captura puede correlacionarse con
la clase.** Toda variación debe repartirse por igual entre las cuatro clases.

| Condición | Criterio |
| --- | --- |
| **Cámara** | La misma cámara y la misma configuración para las cuatro clases. Si se cambia de cámara, se recaptura el conjunto completo, no una clase suelta |
| **Fondo** | Varios fondos, incluido el de la banda simulada. Cada fondo debe aparecer en las cuatro clases. **Nunca un fondo exclusivo de una clase** |
| **Iluminación** | Varias condiciones de luz, todas presentes en las cuatro clases. Si los huevos dañados se fotografían de noche y los buenos de día, el modelo aprenderá la hora del día |
| **Distancia** | Un rango controlado, recorrido por igual en las cuatro clases |
| **Orientación** | Varias orientaciones por huevo, de modo que el defecto aparezca en distintas posiciones del cuadro y no siempre centrado |

Criterios adicionales, ya acordados en
[`03-estrategia-dataset.md`](03-estrategia-dataset.md) sección 5:

- **Registrar el identificador del huevo físico** en cada imagen. Es lo que permitirá aplicar la
  regla de división por grupos y evitar que dos fotos del mismo huevo acaben en particiones
  distintas.
- **No capturar decenas de imágenes casi idénticas**: inflan el conteo sin aportar variedad.
- Si se extraen fotogramas de vídeo, **tratar la secuencia completa como un solo grupo**.
- Para `danado`, cubrir **tipos de daño diversos**: rotura de cáscara, deformación y pérdida de
  integridad.

### 5.4 Uso previsto

1. **Entrenamiento**: junto con el material público aprobado, para que el sistema vea nuestro
   escenario real.
2. **Partición de prueba exclusivamente propia**, con las cuatro clases capturadas en las mismas
   condiciones. Es la única evaluación que mide lo que de verdad importa: cómo se comporta el
   sistema en la banda, no cómo se comporta en las fotos de otro.
3. **Fuente principal** para `sucio` y `danado`, que es lo que ha quedado claro tras la
   validación de licencias.

**El volumen no se fija aquí.** Se determinará cuando se conozcan los conteos reales de las
fuentes públicas aprobadas, para no crear un desbalance artificial entre clases.

---

## 6. Resultado

```
LISTOS PARA DESCARGA:
    1. Egg-Detection (Hugging Face, afshin-dini)
       Licencia MIT, verificada por API el 21/09/2026
       Uso: deteccion `egg` — DATASET COMPLEMENTARIO (51 imagenes; no cubre el minimo de 1000)
       51 imagenes, 423 cajas anotadas, 108 archivos, ~339.47 MiB

    2. Dataset for real-time crack detection on chicken eggs (figshare, INDIGO)
       DOI 10.6084/m9.figshare.21568425.v1
       Licencia CC BY 4.0, verificada por API el 21/09/2026
       Uso: deteccion `egg` + estado `grieta`   |   Atencion: 2,5 GB

    3. Good and Bad Eggs Identification Image Dataset (Mendeley Data)
       DOI 10.17632/mdty358x8m.1
       Licencia CC BY 4.0, verificada por DataCite el 21/09/2026
       Uso: inspeccion como candidato a `bueno`
       Solo las 1.000 originales; las 6.000 aumentadas se excluyen


PENDIENTES DE VERIFICACION:
    Todos los conjuntos de Roboflow Universe, sin excepcion:
      - Cracked-Eggs (fichas A y B)     - licencia + posible duplicado
      - Detection Of cracked eggs       - licencia
      - DIrty Egg                       - licencia
      - dirt stained egg                - licencia
      - Egg Quality Grading             - licencia
      - egg detection final             - licencia + clases desconocidas
      - Egg-count-detection-1           - licencia + numero de imagenes

    Motivo comun: Cloudflare impide leer las fichas de forma automatizada.
    Resolucion: abrir cada ficha manualmente en un navegador y registrar
    aqui la licencia mostrada, con la fecha de consulta.

    Reserva, no pendiente: MMU Egg Grading (Kaggle), licencia ODbL/DbCL
    identificada, descartado por semantica de clases y resolucion.


DESCARTADOS:
      - Eggs image classification: Damaged or not (Kaggle)  - contenido contradictorio
      - egg detection, 519 imagenes (Roboflow)              - ~1.100 clases numericas
      - egg (Ultralytics Platform)                          - 23 imagenes etiquetadas
      - Egg Candling V1.0                                   - ovoscopia, fuera de alcance


DATOS PROPIOS OBLIGATORIOS:
    Las CUATRO clases: bueno, grieta, sucio, danado.

      - sucio y danado : como fuente principal, porque no queda ninguna
                         fuente publica aprobada para ellas
      - bueno y grieta : para el escenario de banda y para la particion de
                         prueba propia
      - las cuatro     : capturadas en condiciones identicas de camara,
                         fondo, iluminacion, distancia y orientacion, para
                         que el modelo no pueda aprender la fuente en lugar
                         del estado del huevo
```

---

## 7. Estado tras este subpaso

- **No se descargó ningún conjunto de datos.** Solo se consultaron metadatos públicos.
- **No se creó ninguna credencial** de Roboflow ni de Kaggle.
- **No se inspeccionó ninguna imagen.**
- `data/raw/` y `data/processed/` siguen vacíos.
- **Tres licencias quedaron verificadas** contra fuentes citables: MIT, CC BY 4.0 y CC BY 4.0.
- **Una licencia quedó identificada con reserva**: ODbL/DbCL en MMU.
- **Ocho conjuntos quedan como LICENCIA NO VERIFICADA**, todos en Roboflow Universe, por un
  bloqueo técnico que requiere intervención manual.

**Siguiente paso (subpaso 7 de la Fase 1):** descargar los tres conjuntos aprobados a
`data/raw/public/`, registrar sus atribuciones e inspeccionar una muestra para validar las
equivalencias de etiquetas que hoy figuran como no validadas.

---

## 8. Actualización por el requisito de 1.000 imágenes reales

> **Trazabilidad.** Inicialmente se seleccionó Egg-Detection como candidato principal; posteriormente, al conocerse el requisito académico de mínimo 1.000 imágenes, se mantuvo como dataset complementario y se amplió la estrategia. El recuadro de la sección 6 se conserva. El detalle está en [`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md).

Egg-Detection **no se borra** ni deja de estar listo para descarga. Con 51 imágenes reales no
puede ser el conjunto principal de entrenamiento. INDIGO (840) + Egg-Detection (51) = **891**,
todavía por debajo del mínimo.

Antes de entrenar, el conjunto de entrenamiento (detección y, por separado, estado) debe
reunir **≥ 1.000 imágenes reales**. El *augmentation* no cuenta. La captura propia sigue
obligatoria y puede completar el recuento junto con fuentes públicas.
