# Estrategia del conjunto de datos

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase: 1 — definición de la estrategia de datos
Documentos relacionados: [`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md) ·
[`02-plan-de-trabajo.md`](02-plan-de-trabajo.md)

> **Este documento define qué datos necesitamos antes de recolectarlos.**
>
> A la fecha **no se ha descargado ningún conjunto de datos**, **no se ha capturado ninguna
> imagen** y **no se ha entrenado ningún modelo**. Todo lo que sigue son criterios de decisión
> acordados por anticipado, para que la recolección y el etiquetado posteriores sean
> consistentes y no haya que rehacerlos.

---

## 1. Tareas de visión

El problema no es una sola tarea de clasificación. Conviene separarlo en tres partes, porque
cada una tiene requisitos de datos distintos y porque la tercera todavía no está definida.

### 1.1 Detección

**Objetivo.** Localizar la presencia y la posición de cada huevo dentro de una imagen o de un
cuadro de video.

| Aspecto | Definición |
| --- | --- |
| Clase inicial | `egg` (una sola clase) |
| Salida esperada | Caja delimitadora (*bounding box*) + confianza |
| Anotación requerida | Caja por cada huevo visible en la imagen |

Se empieza con **una sola clase** a propósito. Detectar "dónde hay un huevo" y decidir "en qué
estado está" son problemas separables, y mezclarlos desde el inicio obliga a que cada clase de
estado tenga suficientes cajas anotadas antes de que el detector funcione siquiera. Con una
clase única, el detector puede entrenarse con todas las imágenes disponibles sin importar el
estado del huevo.

Criterios de anotación para las cajas:

- La caja encierra el huevo completo visible, ajustada al contorno sin margen sobrante.
- Los huevos parcialmente ocluidos o parcialmente fuera del cuadro se anotan igualmente, con
  la caja sobre la porción visible, siempre que el huevo sea reconocible.
- Si en la imagen hay varios huevos, se anotan **todos**, no solo el principal. Dejar huevos
  sin anotar le enseña al modelo que esos objetos son fondo.

### 1.2 Clasificación del estado

**Objetivo.** Determinar la condición de la cáscara de cada huevo detectado.

Estas definiciones son **operativas**: están escritas para que dos personas distintas etiqueten
la misma imagen de la misma forma. Son una **propuesta inicial** y podrán modificarse si el
conjunto de datos real exige una taxonomía distinta.

| Clase | Etiqueta | Definición operativa |
| --- | --- | --- |
| Bueno | `bueno` | Cáscara visualmente íntegra y sin suciedad evidente. |
| Grieta | `grieta` | Existe una fisura visible, pero el huevo conserva en general su forma. |
| Sucio | `sucio` | Existe suciedad visible sobre la cáscara. |
| Dañado | `danado` | Existe rotura importante, deformación evidente o pérdida de integridad. |

**Convención de nombres de etiqueta.** Los identificadores se escriben en minúscula y sin
tildes ni `ñ` (`danado`, no `dañado`). Varios formatos de exportación y herramientas del
ecosistema manejan mal los caracteres no ASCII en nombres de clase y en rutas de archivo. La
forma con tilde se usa únicamente en el texto de la documentación.

**Reglas de desempate**, para resolver los casos ambiguos de forma consistente:

1. Un huevo puede presentar más de una condición a la vez (por ejemplo, sucio *y* agrietado).
   Mientras el esquema de etiquetas sea de clase única, se aplica esta prioridad:
   `danado` > `grieta` > `sucio` > `bueno`. Es decir, prevalece siempre la condición más grave.
2. Si la calidad de la imagen no permite decidir entre dos clases, la imagen **no se etiqueta
   a la fuerza**: se descarta o se aparta para revisión. Una etiqueta dudosa contamina tanto el
   entrenamiento como la evaluación.
3. Si el número de casos con condiciones simultáneas resulta alto, habrá que reconsiderar el
   esquema de clase única y pasar a etiquetas múltiples. Esa decisión se tomará con los datos
   a la vista, no ahora.

### 1.3 Clasificación del tipo — **PENDIENTE DE VALIDACIÓN**

**Estado: PENDIENTE DE VALIDACIÓN.** Esta tarea **se mantiene como requisito propuesto del
proyecto**, pero **no se etiquetará** hasta resolver las preguntas de abajo.

Categorías propuestas en el enunciado: **Triple A**, **Criollo**, **Semicriollo**.

**No deben asumirse como tres clases mutuamente excluyentes.** Existe la sospecha razonable de
que no pertenecen al mismo eje de clasificación, y etiquetar miles de imágenes bajo un supuesto
equivocado obligaría a rehacer todo el trabajo.

Preguntas que deben resolverse antes de etiquetar:

| # | Pregunta | Estado |
| --- | --- | --- |
| 1 | ¿Qué significa cada categoría según fuentes verificables? | Pendiente |
| 2 | ¿"Triple A" representa calibre o tamaño? | Pendiente |
| 3 | ¿Qué representan "criollo" y "semicriollo": origen, raza, tipo de producción? | Pendiente |
| 4 | ¿Son distinguibles visualmente en una fotografía? | Pendiente |
| 5 | ¿Se necesitan atributos separados en lugar de una sola clase? | Pendiente |
| 6 | ¿Hace falta una referencia de escala en la escena? | Pendiente |

Sobre la pregunta 6: **una imagen por sí sola no permite determinar el tamaño físico de un
huevo.** Un huevo pequeño cerca de la cámara y uno grande lejos producen la misma cantidad de
píxeles. Si alguna categoría depende del calibre, la captura tendría que incorporar una de
estas condiciones:

- distancia cámara-objeto fija y conocida, con la cámara en posición constante; o
- un patrón de tamaño conocido dentro del cuadro que sirva de referencia; o
- información externa al sistema de visión, como el peso medido por otro medio.

Resultados posibles de la investigación, y su consecuencia sobre los datos:

| Resultado | Consecuencia |
| --- | --- |
| Las tres son categorías del mismo eje y son excluyentes | Una única etiqueta de tipo por huevo |
| "Triple A" es calibre y las otras dos son origen | Dos atributos independientes, dos etiquetas por huevo |
| Alguna no es distinguible visualmente | Esa categoría se retira o se redefine |
| El calibre requiere escala y no es viable montarla | El atributo de tamaño queda fuera del alcance y se documenta |

Hasta que esto se resuelva, la recolección de imágenes propias debe **registrar el tipo de cada
huevo como metadato** (por ejemplo, en el nombre del archivo o en una hoja de registro), aunque
todavía no se use como etiqueta. Anotar el dato en el momento de la captura cuesta poco;
reconstruirlo después, cuando los huevos ya no están, es imposible.

---

## 2. Fuentes de datos

Se contemplan tres vías. **Todavía no se ha seleccionado ninguna fuente concreta ni se ha
descargado nada**; la búsqueda de conjuntos de datos reales es el paso siguiente.

### 2.1 Conjuntos de datos públicos

Plataformas donde buscar material ya existente y verificable:

- **Roboflow Universe**
- **Kaggle**
- Otras fuentes públicas verificables (repositorios académicos, publicaciones con datos
  abiertos, portales de datos institucionales)

Criterios con los que se evaluará cualquier candidato cuando se realice la búsqueda:

| Criterio | Qué se verifica |
| --- | --- |
| Licencia | Que permita el uso académico y que sea compatible con publicar el proyecto |
| Trazabilidad | Origen identificable, autor y fecha; nada de conjuntos sin procedencia |
| Correspondencia | Que las clases se parezcan a las nuestras; un conjunto de "huevos frescos vs. podridos" no resuelve "grieta vs. sucio" |
| Calidad de anotación | Si trae cajas, que estén bien ajustadas y completas |
| Condiciones de captura | Qué tan parecidas son a nuestro escenario de banda simulada |
| Volumen y balance | Cuántas imágenes **reales** hay por clase. El conjunto de entrenamiento debe tener **como mínimo 1.000 imágenes reales** (requisito académico añadido después de la estrategia inicial; ver [`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md)). 1.000 cajas no equivalen a 1.000 imágenes. El *data augmentation* no cuenta para ese mínimo |

**No se registrará ningún conjunto de datos en este documento hasta haberlo verificado
directamente.** No se listan nombres, enlaces ni cifras de conjuntos que no se hayan revisado.

### 2.2 Imágenes propias

Fotografías y video capturados con nuestra propia cámara, que es la única manera de garantizar
que las imágenes se parezcan a las condiciones reales de operación del sistema. Los criterios
de captura están en la sección 5.

### 2.3 Combinación de ambas

Es la opción más probable: usar material público para dar volumen inicial al detector y material
propio para ajustar el sistema a nuestras condiciones reales.

El conjunto **final** de entrenamiento (público + propio) deberá contener **al menos 1.000
imágenes reales**, y preferiblemente **1.200 a 2.000** si los datos lo permiten. No se exige que
las 1.000 las tome el equipo si existen conjuntos públicos apropiados.

Si se combinan fuentes, hay dos precauciones:

1. **Registrar el origen de cada imagen.** Debe poder reconstruirse de qué fuente vino cada
   archivo, para poder analizar el desempeño por separado y para retirar una fuente completa si
   resulta problemática.
2. **Vigilar el desplazamiento entre fuentes.** Si el conjunto público tiene fondos de estudio y
   el nuestro tiene fondos de mesa, el modelo puede aprender a distinguir la fuente en lugar de
   la clase. La sección 7 lo retoma como comprobación de calidad.

---

## 3. Estructura prevista de los datos

Estructura conceptual propuesta. **Estas carpetas todavía no se crean**: se crearán en el
momento en que existan datos que colocar dentro de ellas.

```
data/
├── raw/                  # Material original, nunca se modifica
│   ├── public/           # Descargado de fuentes públicas, separado por fuente
│   └── own/              # Capturado con nuestra cámara
└── processed/            # Material derivado de raw/, regenerable
```

Más adelante, al exportar el conjunto etiquetado:

```
data/
├── train/                # Partición de entrenamiento
├── validation/           # Partición de validación
└── test/                 # Partición de prueba
```

Razones de esta separación:

- **`raw/` es la fuente de verdad y no se edita nunca.** Cualquier transformación se escribe en
  `processed/`. Si un preprocesamiento sale mal, se vuelve a generar desde `raw/` sin haber
  perdido nada.
- **`public/` y `own/` separados** permiten saber de dónde vino cada imagen sin depender de la
  memoria, evaluar el desempeño por origen y retirar una fuente completa si hace falta.
- **Las particiones son el resultado de una decisión de agrupamiento** (sección 8), no un
  reparto aleatorio de archivos. Por eso viven aparte y se generan al final.

Recordatorio: el contenido de `data/` no se versiona en Git, según lo establecido en
[`../data/README.md`](../data/README.md) y en el `.gitignore` del proyecto.

---

## 4. División del conjunto de datos

### 4.1 Proporción preliminar

| Partición | Proporción | Uso |
| --- | --- | --- |
| Entrenamiento | 70 % | Ajustar los parámetros del modelo |
| Validación | 15 % | Comparar configuraciones y decidir cuándo detener el entrenamiento |
| Prueba | 15 % | Medir el desempeño final, una sola vez, al terminar |

Es una proporción **preliminar** y podrá ajustarse cuando se conozca el volumen real de datos.
Con un conjunto pequeño, un 15 % de prueba puede ser demasiado poco para que las métricas sean
estables, y habría que considerar validación cruzada u otra estrategia.

### 4.2 Si el conjunto público ya trae una división oficial

**Se evaluará primero respetarla.** Muchos conjuntos públicos se publican ya divididos, y sus
autores u otros trabajos reportan resultados sobre esa partición concreta. Rehacer la división
por nuestra cuenta impide comparar nuestros resultados con los de referencia, y además arriesga
mezclar en entrenamiento imágenes que los autores habían apartado deliberadamente para prueba.

Solo se rehará la división si hay una razón documentada, y esa razón quedará escrita aquí.

### 4.3 Sin fuga de información (*data leakage*)

**Regla:** las imágenes derivadas del mismo huevo físico, o de la misma secuencia de video, no
pueden quedar repartidas entre particiones distintas.

**Por qué importa.** Si una foto de un huevo está en entrenamiento y otra foto del *mismo* huevo
está en prueba, el modelo no tiene que aprender a reconocer grietas: le basta con reconocer ese
huevo en particular, que ya vio. La métrica de prueba sale alta, pero esa cifra no dice nada
sobre cómo se comportará el sistema frente a un huevo que nunca ha visto, que es exactamente lo
que hará en la banda. El resultado es un modelo que parece funcionar mucho mejor de lo que
realmente funciona, y el problema solo se descubre al ponerlo en marcha.

El mismo razonamiento aplica, con más fuerza todavía, a los cuadros consecutivos de un video:
dos cuadros separados por una fracción de segundo son prácticamente la misma imagen.

La regla concreta y cómo aplicarla están en la sección 8.

---

## 5. Criterios para la recolección propia

Objetivo: que el conjunto propio tenga **variedad real**, no volumen inflado. Cien imágenes
distintas entre sí valen más que mil imágenes casi idénticas.

### 5.1 Variación que se busca

| Factor | Criterio |
| --- | --- |
| Orientación | Varias orientaciones del mismo huevo: rotarlo sobre su eje mayor y sobre el menor, de modo que el defecto aparezca en posiciones distintas del cuadro |
| Posición | El huevo en distintos lugares del encuadre, no siempre centrado |
| Fondo | Varios fondos distintos, incluyendo alguno parecido al de la banda simulada |
| Iluminación | Condiciones razonablemente variadas: luz natural, luz artificial, con y sin sombras marcadas |
| Distancia | Varias distancias dentro de un rango controlado, coherente con la distancia real de trabajo de la cámara |
| Cantidad por cuadro | Imágenes con un solo huevo y también con varios huevos a la vez |

### 5.2 Qué evitar

- **Decenas de imágenes prácticamente idénticas.** Inflan el conteo sin aportar información y
  sesgan el balance de clases.
- **Un fondo distinto por clase.** Si todos los huevos sucios se fotografían sobre madera y
  todos los buenos sobre tela blanca, el modelo aprenderá el fondo, no el huevo. Cada clase debe
  aparecer sobre varios fondos.
- **Una sola sesión de captura para todo.** La iluminación y el encuadre de una sola sesión
  quedan grabados en el conjunto como si fueran parte del problema.
- **Imágenes desenfocadas o con el defecto fuera de foco**, salvo que se incluyan
  deliberadamente y en proporción pequeña para dar robustez.

### 5.3 Registro durante la captura

Por cada huevo fotografiado conviene anotar, en el nombre del archivo o en una hoja de registro
aparte:

- un **identificador del huevo físico** (indispensable para la regla de la sección 8);
- el estado observado en el momento de la captura;
- el tipo declarado, como metadato (ver sección 1.3);
- la sesión o fecha de captura.

La convención exacta de nombres se definirá y se documentará en
[`../data/README.md`](../data/README.md) al iniciar la captura.

### 5.4 Si se graba video para extraer cuadros

Extraer cuadros de un video es una forma cómoda de obtener muchas imágenes, pero introduce el
riesgo más serio de fuga de información de todo el proyecto:

- Los cuadros consecutivos son casi idénticos. Repartirlos al azar entre entrenamiento,
  validación y prueba equivale a poner la misma imagen en los dos lados del examen.
- **Todos los cuadros extraídos de un mismo video deben ir a la misma partición**, sin
  excepción.
- Conviene además **submuestrear**: tomar un cuadro cada cierto intervalo en lugar de todos,
  para que las imágenes resultantes se diferencien entre sí.
- El identificador del video debe conservarse en el nombre de cada cuadro extraído, para que la
  agrupación pueda aplicarse de forma automática y verificable.

---

## 6. Etiquetado

### 6.1 Herramienta

**Roboflow** se contempla como herramienta de anotación para:

- anotación de cajas delimitadoras;
- organización del conjunto de datos;
- revisión de etiquetas;
- exportación en los formatos que requiera el modelo.

**Todavía no se ha creado ningún proyecto, no se ha conectado ninguna cuenta y no se ha
descargado ni subido nada.** La evaluación de la herramienta y su configuración corresponden a
la fase de etiquetado.

Si se usa una plataforma externa, antes de subir material habrá que revisar dos cosas: las
condiciones de uso aplicables al material que se sube, y que ninguna credencial quede escrita en
el repositorio (para eso existe `.env`, que está excluido del control de versiones).

### 6.2 Consistencia de la anotación

Toda anotación debe seguir los mismos criterios, con independencia de quién la haga y de cuándo:

1. Las definiciones operativas de la sección 1.2 son la referencia; no se etiqueta "por
   intuición".
2. Las reglas de desempate de la sección 1.2 se aplican siempre en el mismo orden.
3. Los casos dudosos se apartan para revisión en lugar de resolverse sobre la marcha.
4. Cualquier criterio nuevo que aparezca durante el etiquetado se escribe en este documento
   **y se aplica retroactivamente** a lo ya etiquetado. Un criterio que cambia a mitad de camino
   produce un conjunto internamente inconsistente.
5. Conviene una revisión de una muestra del material ya etiquetado antes de dar por cerrada la
   anotación.

---

## 7. Comprobaciones de calidad de datos

Verificaciones que deberán ejecutarse **cuando exista el conjunto de datos**, antes de entrenar.
Ninguna se ha ejecutado todavía porque no hay datos.

| # | Comprobación | Qué se busca |
| --- | --- | --- |
| 1 | Imágenes corruptas | Archivos que no abren, truncados o con extensión que no corresponde al contenido |
| 2 | Duplicados | El mismo archivo repetido, por descarga doble o por combinar fuentes |
| 3 | Imágenes demasiado similares | Casi duplicados, típicamente cuadros vecinos de un video; alimentan el riesgo de fuga |
| 4 | Resolución | Imágenes por debajo del mínimo útil, o con relaciones de aspecto muy dispares |
| 5 | Clases desbalanceadas | Conteo por clase; una clase muy minoritaria produce métricas engañosas |
| 6 | Etiquetas incorrectas | Revisión de una muestra: clase equivocada, cajas mal ajustadas, huevos sin anotar |
| 7 | Sesgo por fondo | Que una clase no esté asociada a un único fondo o a una única sesión de captura |
| 8 | Iluminación | Distribución de brillo y contraste; imágenes quemadas o demasiado oscuras |
| 9 | Oclusiones | Cuántos huevos aparecen parcialmente tapados y si el criterio de anotación fue uniforme |

Los resultados de estas comprobaciones se documentarán con los conteos reales obtenidos. **No se
anticipa ninguna cifra en este documento.**

---

## 8. Principio rector: agrupar por huevo y por secuencia

Es el principio más importante de toda la estrategia de datos.

> **La división en entrenamiento, validación y prueba se hace por grupos, no por archivos
> sueltos. Todas las imágenes derivadas del mismo huevo físico o de la misma secuencia de video
> deben quedar en la misma partición.**

Procedimiento:

1. Asignar a cada imagen un **identificador de grupo**: el huevo físico que aparece en ella o,
   si viene de un video, el video de origen.
2. Repartir los **grupos** —no las imágenes— entre las tres particiones, respetando la
   proporción de la sección 4.1 de forma aproximada.
3. Comprobar después del reparto que ningún identificador de grupo aparece en más de una
   partición. Esta verificación debe quedar registrada.

**Por qué.** Sin esta regla, el modelo puede alcanzar métricas altas en prueba simplemente
porque ya vio el mismo huevo durante el entrenamiento, sin haber aprendido nada generalizable.
El resultado es un sistema que parece funcionar mucho mejor de lo que realmente funciona, y la
diferencia solo aparece cuando se pone frente a huevos nuevos. Para un proyecto cuyo objetivo es
medir honestamente el desempeño, una métrica inflada es peor que una métrica baja.

Efecto secundario aceptado: la proporción 70/15/15 no saldrá exacta, porque los grupos no tienen
todos el mismo tamaño. Se prefiere una proporción aproximada y una evaluación honesta antes que
una proporción exacta y una evaluación contaminada.

---

## 9. Estado al cierre de esta fase

Lo que queda establecido:

- El problema está separado en tres tareas con requisitos de datos distintos.
- La detección arranca con una sola clase, `egg`, con salida de caja delimitadora y confianza.
- Las cuatro clases de estado tienen definición operativa, convención de nombres y reglas de
  desempate.
- Están definidos los criterios con los que se evaluará cualquier fuente de datos.
- Está definida la estructura de carpetas prevista y la proporción preliminar de las particiones.
- El conjunto de entrenamiento deberá tener **≥ 1.000 imágenes reales** (objetivo 1.200–2.000).
  Este requisito se añadió después de redactar la estrategia inicial; el detalle está en
  [`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md).
- Están definidos los criterios de captura propia y las comprobaciones de calidad pendientes.
- Está establecida la regla de agrupación por huevo y por secuencia.

Lo que **todavía no existe ni se ha hecho**:

- **No existe un conjunto de datos definitivo.**
- **No se ha descargado ningún conjunto de datos.**
- **No se ha capturado ninguna imagen propia.**
- **No se ha etiquetado nada.**
- **No se ha entrenado ningún modelo.**
- **No se ha medido ninguna métrica.**
- **Las clases de estado son una propuesta inicial** y podrán cambiar si los datos reales lo
  exigen.
- **La clasificación por tipo está PENDIENTE DE VALIDACIÓN** (sección 1.3) y no se etiquetará
  hasta resolverla.

**Siguiente paso:** investigar conjuntos de datos públicos reales y verificables, evaluarlos con
los criterios de la sección 2.1, y registrar aquí los hallazgos con su procedencia.
