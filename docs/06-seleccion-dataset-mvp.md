# Selección del conjunto de datos para el MVP

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase 1, subpaso 5: seleccionar los conjuntos de datos del MVP
Documentos relacionados: [`04-investigacion-datasets.md`](04-investigacion-datasets.md) ·
[`05-taxonomia-clasificacion.md`](05-taxonomia-clasificacion.md) ·
[`03-estrategia-dataset.md`](03-estrategia-dataset.md)

> **No se ha descargado nada.** Este documento es una decisión de selección. No se usaron APIs,
> no se descargaron archivos comprimidos, no se crearon credenciales de Roboflow y no se movió
> ninguna imagen. `data/` sigue vacío.

---

## 0. Alcance de esta selección

Se seleccionan conjuntos de datos **únicamente para las dos tareas del MVP** definidas en
[`05-taxonomia-clasificacion.md`](05-taxonomia-clasificacion.md):

1. **Detección** de huevos, clase única `egg`, con caja delimitadora y confianza.
2. **Clasificación del estado visual**: `bueno`, `grieta`, `sucio`, `danado`.

**Quedan expresamente fuera de esta selección** el eje de origen (`criollo`, `semicriollo`) y el
eje de calibre (Triple A), por ser experimental y extensión futura respectivamente. No se elige
ningún conjunto de datos para ellos.

**Todos los candidatos evaluados provienen de
[`04-investigacion-datasets.md`](04-investigacion-datasets.md).** No se incorpora ningún conjunto
nuevo en este paso.

### Advertencia sobre la calidad de la información

Las fichas de Roboflow Universe y Kaggle **no se pudieron abrir directamente** durante la
investigación (Cloudflare y reCAPTCHA), y **no se ha visto ninguna imagen de ningún conjunto**.
Por tanto, en este documento:

- Los campos **resolución**, **fondos** y **variedad visual** están marcados como *no verificado*
  en casi todos los casos, porque ninguna ficha los publica y no se ha inspeccionado el material.
- La **calidad aparente de las anotaciones** se infiere de señales indirectas (existencia de un
  modelo entrenado, número de descargas, coherencia de los nombres de clase), **no de haber
  revisado las cajas**.
- Toda la selección es **provisional y condicionada** a las verificaciones de la sección 7.

---

## 1. Evaluación de los candidatos para **detección**

### 1.1 Egg-Detection (Hugging Face)

| Criterio | Evaluación |
| --- | --- |
| URL | https://huggingface.co/datasets/afshin-dini/Egg-Detection |
| Número de imágenes | **51** (49 en `train`, 2 en `val`) |
| Instancias anotadas | **423 cajas** (393 en `train`, 30 en `val`), unas 8 por imagen |
| Archivos totales | 108 (51 imágenes, 51 etiquetas, 6 de configuración) |
| Tamaño | 339,47 MiB ≈ 355,96 MB |
| Clases | **PENDIENTE DE VERIFICACIÓN** hasta leer `data/data.yaml`. La ficha sugiere dos clases por color de cáscara |
| Cajas delimitadoras | **Sí**, formato YOLO |
| Tipo de tarea | Detección de objetos |
| Calidad aparente de las anotaciones | **Indicios favorables**: hay un modelo entrenado y publicado sobre este conjunto, un repositorio de código asociado y 322 descargas en el último mes. **No verificado por inspección** |
| Licencia | **MIT** — confirmada en la propia ficha del conjunto |
| Resolución | No especificado por la fuente |
| Fondos | Declarados por el autor como variados a propósito: bandeja de plástico transparente, cartón claro y cartón oscuro. **No verificado** |
| Variedad visual | Varios colores de cáscara y varios tipos de bandeja. Escenas de huevos en bandeja o caja |
| Compatibilidad con nuestro objetivo | **Alta.** Cualquiera que sea el nombre de sus clases, todas designan huevos y se fusionan en nuestra clase única `egg` sin ambigüedad |
| Limitaciones | **Solo 51 imágenes.** División original de 49 en `train` y 2 en `val`, **sin partición de prueba y con una validación inservible**. Escenario de bandeja, **no de banda transportadora** |

### 1.2 Egg-count-detection-1 (Roboflow Universe)

| Criterio | Evaluación |
| --- | --- |
| URL | https://universe.roboflow.com/data-science-devhu/egg-count-detection-1 |
| Número de imágenes | **No especificado por la fuente** |
| Clases | `Egg` (una sola) |
| Cajas delimitadoras | Sí |
| Tipo de tarea | Detección de objetos |
| Calidad aparente de las anotaciones | **No verificable.** La ficha no publica métricas ni descargas |
| Licencia | **No especificado por la fuente** |
| Resolución | No especificado por la fuente |
| Fondos | Escenario declarado de banda transportadora en planta de producción. **No verificado** |
| Variedad visual | No verificable |
| Compatibilidad con nuestro objetivo | **La más alta en concepto**: es el único candidato cuyo escenario declarado coincide con el nuestro, y su clase única `Egg` es idéntica a nuestro esquema |
| Limitaciones | **Dos datos esenciales desconocidos: cuántas imágenes tiene y bajo qué licencia se publica.** Sin ellos no puede seleccionarse como principal |

### 1.3 Dataset for real-time crack detection on chicken eggs (INDIGO, UIC)

| Criterio | Evaluación |
| --- | --- |
| URL | https://doi.org/10.6084/m9.figshare.21568425.v1 |
| Número de imágenes | 840 (740 de entrenamiento, 100 de prueba) |
| Clases | `egg` y `crack` |
| Cajas delimitadoras | Sí |
| Tipo de tarea | Detección de objetos |
| Calidad aparente de las anotaciones | **Indicios favorables**: procede de un repositorio universitario, tiene autoría identificable (Botta y Datta), DOI y una cita. **No verificado por inspección** |
| Licencia | **No especificado por la fuente consultada** (la página exige JavaScript) |
| Resolución | No especificado por la fuente |
| Fondos | No especificado por la fuente |
| Variedad visual | No verificable |
| Compatibilidad con nuestro objetivo | **Doble**: su clase `egg` sirve para detección y su clase `crack` sirve para el estado `grieta`. Es el único candidato que aporta a las dos tareas del MVP a la vez |
| Limitaciones | Licencia sin confirmar, que es bloqueante. Solo cubre grietas |

### 1.4 egg detection final (Roboflow Universe)

| Criterio | Evaluación |
| --- | --- |
| URL | https://universe.roboflow.com/egg-detection-mnb0n/egg-detection-final |
| Número de imágenes | 604 |
| Clases | **No especificado por la fuente** |
| Cajas delimitadoras | Sí |
| Tipo de tarea | Detección de objetos |
| Calidad aparente de las anotaciones | **Indicio favorable**: tiene un modelo YOLOv8s asociado y 110 descargas. **No verificado** |
| Licencia | **CC BY 4.0** — confirmada |
| Resolución | No especificado por la fuente |
| Fondos | No especificado por la fuente |
| Variedad visual | No verificable |
| Compatibilidad con nuestro objetivo | **Indeterminada**: sin saber qué clases contiene no puede afirmarse que sus etiquetas sirvan |
| Limitaciones | La ficha no tiene descripción ni lista de clases publicada |

### 1.5 Candidatos descartados para detección

| Conjunto | Motivo del descarte |
| --- | --- |
| egg detection (519 imágenes) | Aproximadamente 1.100 clases con nombres numéricos sin significado (`05517`, `05518`…). Requeriría re-etiquetar desde cero |
| egg (Ultralytics Platform) | 718 imágenes pero solo 23 etiquetadas y 75 anotaciones. Además fondo único (superficies rojas estampadas), candidato claro a sesgo |
| Egg Candling V1.0 | Es ovoscopía: inspección interna por transiluminación. Fuera del alcance declarado del proyecto |

---

## 2. Decisión de detección

**Conjunto principal: Egg-Detection de Hugging Face.**

Se elige por una razón que ninguno de los demás cumple: **es el único con licencia permisiva
confirmada en su propia ficha** (MIT). En un trabajo académico que se va a publicar en GitHub,
una licencia verificada no es un detalle administrativo, es un requisito. A eso se suma que viene
en formato YOLO listo para usar, que tiene un modelo y un repositorio de código de referencia
—señal de que las anotaciones funcionan— y que su autor declara haber buscado variedad de fondos
a propósito.

**El volumen de imágenes es pequeño: 51.** Lo que amortigua esa cifra es que cada imagen contiene
varios huevos, de modo que el conjunto aporta **423 instancias anotadas**, unas 8 por imagen. Para
un detector de una sola clase, con un objeto de forma tan regular como un huevo, 423 ejemplos de
objeto son un punto de partida utilizable.

Conviene sostener las dos afirmaciones a la vez, porque tiran en direcciones distintas: **hay
pocas imágenes pero bastantes objetos anotados**. Lo primero limita la variedad de escenas, los
fondos y las condiciones de luz que el modelo llega a ver; lo segundo le da suficientes ejemplos
de la forma «huevo» como para aprenderla. El resultado es un conjunto válido como **línea base
para la detección**, y claramente insuficiente como fuente única.

> **Corrección.** Una versión anterior de este documento afirmaba que el conjunto tenía 423
> imágenes y que las cajas serían «sustancialmente más». Era incorrecto en los dos extremos: 423
> era ya el recuento de cajas, y las imágenes son 51. Ver la comprobación en
> [`04-investigacion-datasets.md`](04-investigacion-datasets.md), sección 1.1.

### ¿Es suficiente por sí solo? No

**No lo es, por dos razones distintas: el escenario y el volumen.**

Por escenario: las imágenes son de huevos en bandeja y en caja de cartón, mientras que nuestro
sistema verá huevos pasando sobre una banda simulada, con nuestra iluminación, nuestra cámara y
nuestro fondo. Un detector entrenado solo con bandejas puede dar buenas métricas en validación y
comportarse peor frente a nuestra escena real.

Por volumen: 51 imágenes cubren muy pocas situaciones distintas, y la división original deja 2
imágenes para validar, lo que no permite medir nada con sentido. **Habrá que rehacer la división
en `train` / `validation` / `test`** durante la preparación del conjunto, respetando la regla de
agrupación por huevo físico de [`03-estrategia-dataset.md`](03-estrategia-dataset.md). No se crea
ninguna partición todavía.

**Conviene combinarlo con capturas propias**, con dos funciones distintas:

1. **Ajuste al escenario**: añadir imágenes de huevos sobre la banda simulada al conjunto de
   entrenamiento, para que el detector vea nuestro fondo y nuestra geometría.
2. **Evaluación honesta**: reservar una partición de prueba compuesta **exclusivamente por
   imágenes propias**, además de la partición mixta. Es la única forma de saber si el sistema
   funciona en la escena en la que va a operar, y no solo en la escena en la que se entrenó.

**Complementos públicos, condicionados a verificación:** si se confirma su licencia y su tamaño,
*Egg-count-detection-1* sería una incorporación muy valiosa por ser el único con escenario de
banda. Y si se confirma la licencia del conjunto de INDIGO, sus 840 imágenes con clase `egg`
aportarían volumen y, de paso, cubrirían la clase `grieta`.

---

## 3. Evaluación de los candidatos para **estado**

### 3.1 Resumen de los candidatos

| Conjunto | Imágenes | Clases | Cajas | Tarea | Licencia | Aporta a |
| --- | --- | --- | --- | --- | --- | --- |
| Crack detection (INDIGO) | 840 | `egg`, `crack` | Sí | Detección | **Sin confirmar** | `grieta` |
| Cracked-Eggs (Roboflow) | 690 | `cracked-egg`, `normal-egg` | Sí | Detección | CC BY 4.0 | `grieta`, `bueno` |
| Detection Of cracked eggs | ~1.200 | `Brown cracked egg`, `white cracked egg` | Sí | Detección | CC BY 4.0 | `grieta` (solo positivos) |
| DIrty Egg | 609 | `Dirty-samples` | No | Clasificación | **Sin confirmar** | `sucio` |
| dirt stained egg | 103 | 1 clase | Sí | Detección | CC BY 4.0 | `sucio` |
| Egg Quality Grading | ~1.100 | 5, mezcladas | Sí | Detección | CC BY 4.0 | `sucio` (parcial) |
| Good and Bad Eggs (Mendeley) | 1.000 + 6.000 aum. | binaria | No | Clasificación | CC BY 4.0 | `bueno` (parcial) |
| MMU Egg Grading (Kaggle) | 3.641 → 5.580 | 6 grados AA–E | Sí (YOLO) | Ambas | "Open Database" | Indeterminado |

En todos ellos: **resolución, fondos y variedad visual no verificados**, salvo MMU Egg Grading,
cuya ficha declara 224 × 224 px y variedad de iluminación, fondos y ángulos.

### 3.2 Observaciones críticas sobre candidatos concretos

**Cracked-Eggs aparece en dos fichas distintas** (`eggs-u2ctb/cracked-eggs-gxbbf` y
`crackedeggs/cracked-eggs`), ambas con exactamente 690 imágenes y exactamente las mismas dos
clases, pero con autores distintos. **Es muy probable que sea el mismo material duplicado.** Debe
usarse **una sola de las dos fichas**. Tomarlas como fuentes independientes introduciría
duplicados masivos y, con ellos, fuga de información entre particiones.

**Detection Of cracked eggs tiene sus dos clases agrietadas** (`Brown cracked egg` y
`white cracked egg`, diferenciadas por color de cáscara). **No contiene huevos sanos.** Solo
puede usarse como fuente de ejemplos positivos de `grieta`, fusionando sus dos clases. Además su
contador de vistas y descargas está en cero, lo que significa que nadie lo ha revisado.

**Egg Quality Grading mezcla ejes**: junta color de cáscara (blanco, marrón) con defectos
(manchado de sangre, manchado de suciedad, depósitos de calcio) en un mismo conjunto de
etiquetas. Es el mismo error conceptual que corregimos en nuestra propia taxonomía. Solo su
subconjunto `dirt-stained` es aprovechable, y habría que extraerlo.

**MMU Egg Grading no se selecciona**, pese a ser el conjunto más grande con anotaciones YOLO. Sus
seis grados AA–E son **grados de una escala de calidad ajena**, que no se corresponden con
nuestras cuatro clases y cuyo significado no está documentado en la ficha. Remapearlos sería
adivinar. Además su resolución de 224 × 224 px es dudosa para detectar una fisura fina. **Queda
como reserva**, a revisar si la cobertura de las clases resulta insuficiente.

**Good and Bad Eggs: usar solo las 1.000 imágenes originales.** Las 6.000 aumentadas derivan de
ellas; mezclarlas entre particiones produciría fuga de información directa.

**Eggs image classification: Damaged or not (Kaggle) se descarta.** Tres artículos publicados que
declaran usarlo se contradicen sobre su contenido: uno dice 794 imágenes en dos clases de daño,
otro dice 794 en tres clases de tipo de gallina, y un tercero dice 7.392 imágenes. Inutilizable
hasta verificarlo directamente.

---

## 4. Cobertura de clases y remapeo de etiquetas

### 4.1 Tabla de cobertura

| Clase nuestra | Conjunto que la cubre | Etiqueta original | ¿Requiere remapeo? | ¿Equivalencia verificada? |
| --- | --- | --- | --- | --- |
| `bueno` | Cracked-Eggs | `normal-egg` | **Sí** | **No.** Ver 4.2 |
| `bueno` | Good and Bad Eggs | clase "good" (binaria) | **Sí** | **No.** Ver 4.2 |
| `grieta` | Crack detection (INDIGO) | `crack` | **Sí** | **No.** Ver 4.3 |
| `grieta` | Cracked-Eggs | `cracked-egg` | **Sí** | **No.** Ver 4.3 |
| `grieta` | Detection Of cracked eggs | `Brown cracked egg` + `white cracked egg` | **Sí**, fusionando ambas | **No.** Ver 4.3 |
| `sucio` | DIrty Egg | `Dirty-samples` | **Sí** | **No.** Ver 4.4 |
| `sucio` | dirt stained egg | etiqueta única del proyecto | **Sí** | **No.** Ver 4.4 |
| `sucio` | Egg Quality Grading | `dirt-stained` (extrayendo solo esa clase) | **Sí** | **No.** Ver 4.4 |
| `danado` | **Ninguno** | — | — | — |

### 4.2 Por qué `normal-egg` → `bueno` no es una equivalencia segura

Nuestra definición de `bueno` es "cáscara visualmente íntegra **y sin suciedad evidente**". Es
una definición con **dos condiciones**.

Los conjuntos de grietas solo declaran una: `normal-egg` significa, en su contexto, "huevo no
agrietado". **Nada garantiza que sus huevos "normales" estén limpios.** Un huevo sin grietas pero
con suciedad sería `normal-egg` para ellos y `sucio` para nosotros.

El riesgo es concreto: si se importan como `bueno` unos cientos de huevos que en realidad están
sucios, el modelo recibe señales contradictorias entre las clases `bueno` y `sucio`, que es
justamente el par que más nos interesa separar. **Requiere inspección visual de una muestra antes
de aceptar el remapeo.**

Existe un precedente publicado que resuelve esto con un umbral objetivo: el trabajo de ISPRS
recogido en `04-investigacion-datasets.md`, sección 2.9, considera "normal" a un huevo cuyas
manchas no cubran más de 1/32 de la superficie. Adoptar un umbral explícito de ese tipo sería
preferible a un criterio intuitivo.

### 4.3 Por qué `cracked-egg` → `grieta` no es una equivalencia segura

Nuestra taxonomía **separa** `grieta` de `danado`: la primera es una fisura visible con el huevo
conservando su forma; la segunda es rotura importante, deformación o pérdida de integridad.

Los conjuntos públicos usan una sola etiqueta, `cracked` o `crack`, que **probablemente cubre
ambas situaciones**. Importarla entera como `grieta` metería huevos rotos en la clase equivocada
y contaminaría precisamente la frontera que necesitamos que el modelo aprenda.

**Requiere inspección.** Hay dos salidas posibles, a decidir con las imágenes delante: separar
manualmente los casos severos hacia `danado`, o aceptar la etiqueta original y documentar
expresamente que la frontera entre ambas clases queda difusa en el material importado.

### 4.4 Por qué las etiquetas de suciedad no son equivalencias seguras

Ninguna de las tres fuentes de suciedad **declara un umbral**: no dicen cuánta suciedad hace que
un huevo sea "sucio". Los criterios entre fuentes pueden diferir, y diferir del nuestro.

Además `Dirty-samples` es una **clase única sin contraparte**: aporta solo ejemplos positivos.
Para entrenar un clasificador hacen falta también ejemplos negativos comparables, y esos vendrían
de otro conjunto distinto, lo que nos lleva al problema de la sección 5.2.

---

## 5. Datos faltantes y riesgos de la combinación

### 5.1 La clase `danado` no tiene ninguna cobertura pública

Es el vacío más claro de toda la investigación. `danado` **no aparece en ningún conjunto
descargable**; solo figura como "broken shell" en conjuntos privados descritos en artículos, que
no están publicados.

**Propuesta: captura propia controlada.** Es la clase más fácil de generar deliberadamente, y
además la que menos depende de conseguir material ajeno: basta dañar algunos huevos a propósito y
fotografiarlos siguiendo los criterios ya definidos en
[`03-estrategia-dataset.md`](03-estrategia-dataset.md), sección 5.

Criterios que debería cumplir esa captura, todos ya acordados en la estrategia:

- Varias orientaciones por huevo, de modo que el daño aparezca en posiciones distintas del cuadro.
- Varios fondos, incluido el de la banda simulada. **Nunca un fondo exclusivo para esta clase**,
  o el modelo aprenderá el fondo en lugar del daño.
- Iluminación variada.
- Identificador del huevo físico registrado, para la regla de agrupación por grupos.
- Tipos de daño diversos: rotura de cáscara, deformación, pérdida de integridad.

**El volumen no se fija aquí.** Se determinará en función de los conteos reales de las otras tres
clases, para no crear un desbalance artificial. Fijar un número ahora, sin saber cuántas imágenes
aportará cada fuente pública, sería inventar una cifra.

### 5.2 El riesgo más serio: que el modelo aprenda el origen y no la clase

Esta es la principal consecuencia técnica de tener que combinar fuentes, y conviene que quede
escrita antes de descargar nada.

Si `bueno` viene de un conjunto, `grieta` de otro, `sucio` de un tercero y `danado` de nuestras
propias fotos, entonces **cada clase tiene una fuente distinta**. Y cada fuente tiene su propia
cámara, iluminación, fondo y resolución. En esas condiciones, **la fuente se convierte en un
predictor perfecto de la clase**: al modelo le basta reconocer "esto parece una foto del conjunto
A" para acertar la etiqueta, sin haber mirado nunca el huevo.

El resultado sería un modelo con métricas excelentes en prueba y comportamiento errático en la
banda real, porque allí las cuatro clases llegan con la misma cámara y el mismo fondo, y la
pista en la que se apoyaba desaparece.

**Mitigaciones, que deben planificarse desde ya:**

1. **Capturar las cuatro clases nosotros**, bajo condiciones idénticas, no solo `danado`. Es la
   mitigación de fondo: un subconjunto propio donde la fuente no aporte información sobre la
   clase.
2. **Partición de prueba exclusivamente propia**, con las cuatro clases capturadas en las mismas
   condiciones. Es la única evaluación que mide lo que nos importa.
3. **Registrar el origen de cada imagen** como metadato, para poder medir el desempeño por fuente
   y detectar el problema si aparece.
4. **Homogeneizar** en lo posible el preprocesamiento entre fuentes, aunque esto solo reduce el
   efecto, no lo elimina.

Esto **no invalida el uso de material público**: sirve para dar volumen al detector y para
preentrenar el clasificador. Pero significa que **la captura propia no es un complemento
opcional, sino parte del camino crítico del MVP**.

### 5.3 Resumen de la cobertura

| Clase | Cobertura pública | Origen propio necesario |
| --- | --- | --- |
| `bueno` | Aceptable, pendiente de verificar la definición | Sí, para el escenario y la prueba |
| `grieta` | Buena en volumen, pendiente de separar de `danado` | Sí, para el escenario y la prueba |
| `sucio` | Escasa (unas 700 imágenes entre dos fuentes, sin umbral declarado) | Sí, para el escenario y la prueba |
| `danado` | **Nula** | **Sí, obligatorio como fuente principal** |

---

## 6. Decisión

```
DATASET DE DETECCIÓN:
    Egg-Detection (Hugging Face, afshin-dini) — licencia MIT, formato YOLO
    https://huggingface.co/datasets/afshin-dini/Egg-Detection
    51 imagenes con 423 cajas anotadas. Linea base, insuficiente por si sola.

    Complementos condicionados a verificar licencia y tamaño:
      - Egg-count-detection-1 (Roboflow) — único con escenario de banda transportadora
      - Dataset for real-time crack detection on chicken eggs (INDIGO) — clase `egg`

DATASET(S) DE ESTADO:
    grieta  → Dataset for real-time crack detection on chicken eggs (INDIGO), clase `crack`
              [condicionado a verificar licencia]
            → Cracked-Eggs (Roboflow, UNA sola de las dos fichas), clase `cracked-egg`
            → Detection Of cracked eggs (Roboflow), solo como ejemplos positivos

    bueno   → Cracked-Eggs, clase `normal-egg`
            → Good and Bad Eggs (Mendeley), SOLO las 1.000 imágenes originales

    sucio   → DIrty Egg (Roboflow), clase `Dirty-samples`
              [condicionado a verificar licencia]
            → dirt stained egg (Roboflow)
            → Egg Quality Grading (Roboflow), extrayendo solo la clase `dirt-stained`

    danado  → NINGUNO. Sin cobertura pública.

    Reserva, no seleccionado: MMU Egg Grading (Kaggle)
    Descartado: Eggs image classification: Damaged or not (Kaggle)

DATOS PROPIOS NECESARIOS:
    SÍ.

    Obligatorio como fuente principal:
      - danado  (no existe alternativa pública)

    Obligatorio para el escenario y para la partición de prueba:
      - bueno, grieta, sucio, danado  (las cuatro, en condiciones idénticas,
        sobre la banda simulada)
```

### Por qué esta decisión

**Para detección se elige Egg-Detection** porque es el único candidato con licencia permisiva
verificada en su propia ficha, viene en formato YOLO listo para usar y tiene un modelo de
referencia que sugiere que sus anotaciones funcionan. Sus clases se fusionan en `egg` sin
ambigüedad, sea cual sea su nombre definitivo. Aporta **51 imágenes con 423 cajas anotadas**:
sirve como línea base del detector, pero **habrá que complementarlo** con el conjunto de INDIGO
y con capturas propias del escenario de banda.

**Para el estado no se elige un conjunto, sino una combinación**, porque **ninguno de los
candidatos contiene las cuatro clases**. La combinación propuesta cubre tres de ellas con
material público y deja la cuarta a captura propia.

**Se exige captura propia de las cuatro clases** y no solo de `danado` por el razonamiento de la
sección 5.2: si cada clase viene de una fuente distinta, el modelo puede aprender a reconocer la
fuente en lugar del huevo, y las métricas dejarían de significar nada.

**Ninguna equivalencia de etiquetas se da por buena.** Las tres que se proponen —`normal-egg` a
`bueno`, `cracked` a `grieta`, las etiquetas de suciedad a `sucio`— quedan marcadas como **no
verificadas** y sujetas a inspección visual antes de aceptarlas.

---

## 7. Verificaciones obligatorias antes de descargar

Esta selección es **provisional**. Antes de traer un solo archivo hay que resolver:

| # | Verificación | Conjunto afectado | Bloqueante |
| --- | --- | --- | --- |
| 1 | Confirmar la licencia | INDIGO, DIrty Egg, Egg-count-detection-1 | **Sí.** Sin licencia compatible, no se usa |
| 2 | Comprobar si las dos fichas de Cracked-Eggs son el mismo material | Cracked-Eggs | **Sí.** Usar ambas duplicaría datos |
| 3 | Confirmar el número de imágenes | Egg-count-detection-1 | Sí, para poder valorarlo |
| 4 | Confirmar qué clases contiene | egg detection final | Sí, si se quiere incorporar |
| 5 | Inspeccionar una muestra y validar las equivalencias de etiquetas | Todos los de estado | **Sí.** Ver secciones 4.2 a 4.4 |
| 6 | Revisar resolución y fondos reales | Todos | Sí, para estimar el desplazamiento de dominio |
| 7 | Verificar solapamiento entre conjuntos | Todos los de grietas | Sí, para evitar duplicados cruzados |

---

## 8. Estado tras este subpaso

- **No se ha descargado ningún conjunto de datos.**
- **No se usaron APIs ni se crearon credenciales de Roboflow.**
- **No se ha capturado ninguna imagen propia.**
- **No se ha inspeccionado ninguna imagen de ningún conjunto.**
- `data/raw/` y `data/processed/` siguen vacíos.
- La selección queda **decidida pero condicionada** a las siete verificaciones de la sección 7.

**Siguiente paso (subpaso 6 de la Fase 1):** resolver las verificaciones bloqueantes —licencias y
duplicación— y, en paralelo, preparar la captura propia empezando por la clase `danado`, que es
la que no tiene ninguna alternativa pública.
