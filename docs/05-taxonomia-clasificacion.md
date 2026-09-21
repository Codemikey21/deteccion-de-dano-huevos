# Taxonomía de clasificación y alcance del sistema

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fase 1, subpasos 3 y 4: validar las categorías y decidir qué información puede obtenerse
visualmente
Documentos relacionados: [`04-investigacion-datasets.md`](04-investigacion-datasets.md) ·
[`03-estrategia-dataset.md`](03-estrategia-dataset.md) ·
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md)

> Este documento resuelve **qué debe predecir el sistema y qué datos necesita cada predicción**.
> No se ha descargado ningún conjunto de datos, no se ha capturado ninguna imagen y no se ha
> entrenado ningún modelo.

---

## 0. Punto de partida

El enunciado original del proyecto planteaba la clasificación del huevo como **dos variables**:
un estado y un tipo, donde el tipo agrupaba *Triple A*, *criollo* y *semicriollo* como si fueran
tres opciones de una misma lista.

La investigación documentada en [`04-investigacion-datasets.md`](04-investigacion-datasets.md)
mostró que ese agrupamiento no se sostiene. Dos hechos lo obligan a cambiar:

1. **"Triple A" es una categoría de peso.** La norma técnica colombiana NTC 1240 clasifica el
   huevo fresco de gallina por gramos. *Triple A* no describe el aspecto del huevo: describe
   cuánto pesa. (Las cifras concretas están en `04-investigacion-datasets.md`, sección 3.2, y
   **provienen de fuentes secundarias coincidentes, no del texto oficial de la norma**.)
2. **"Criollo" y "semicriollo" describen el origen o el tipo de producción del ave**, no su peso.

Un huevo criollo tiene además un calibre, y un huevo Triple A tiene además un origen. Las
categorías no son alternativas entre sí: **son atributos distintos que coexisten en el mismo
huevo**. Tratarlas como una sola lista de tres opciones produciría un conjunto de etiquetas
lógicamente imposible de satisfacer.

Este documento las separa en tres ejes independientes y decide qué hace el proyecto con cada uno.

---

## 1. Los tres ejes de clasificación

### 1.1 Eje A — Estado visual del huevo

**Pregunta que responde:** ¿en qué condición está la cáscara de este huevo?

| Categoría | Etiqueta | Definición operativa |
| --- | --- | --- |
| Bueno | `bueno` | Cáscara visualmente íntegra y sin suciedad evidente |
| Grieta | `grieta` | Existe una fisura visible, pero el huevo conserva en general su forma |
| Sucio | `sucio` | Existe suciedad visible sobre la cáscara |
| Dañado | `danado` | Existe rotura importante, deformación evidente o pérdida de integridad |

Las definiciones y las reglas de desempate para huevos con más de una condición están en
[`03-estrategia-dataset.md`](03-estrategia-dataset.md), sección 1.2.

**¿Es observable por una cámara?** Sí. Una grieta, una mancha de suciedad y una rotura son
**alteraciones de la superficie visible** del huevo. Toda la información necesaria para decidir
la clase está contenida en la imagen, sin depender de ningún instrumento adicional. Este es el
único de los tres ejes del que puede afirmarse esto sin reservas.

**¿Hay datos?** Sí, parcialmente, según la sección 6.3 de
[`04-investigacion-datasets.md`](04-investigacion-datasets.md): `bueno` y `grieta` tienen
cobertura pública suficiente, `sucio` tiene cobertura escasa (alrededor de 700 imágenes entre dos
fuentes) y `danado` **no tiene cobertura pública**. Esto último se discute en la sección 2.4.

**Decisión: eje OBLIGATORIO.** Es el núcleo del proyecto.

### 1.2 Eje B — Tipo u origen visual

**Pregunta que responde:** ¿de qué tipo de producción proviene este huevo?

| Categoría candidata | Etiqueta propuesta | Estado |
| --- | --- | --- |
| Criollo | `criollo` | Candidata, viabilidad por determinar |
| Semicriollo | `semicriollo` | Candidata, viabilidad por determinar |

**Advertencia central: no se afirma que estas categorías puedan distinguirse correctamente
mediante visión artificial.** No hay evidencia que lo respalde, y sí hay indicios de lo
contrario.

La viabilidad de este eje depende de cuatro condiciones, ninguna de las cuales está satisfecha
hoy:

| Condición | Estado actual |
| --- | --- |
| Existe un conjunto de datos disponible | **No.** No existe ningún conjunto público etiquetado como criollo o semicriollo (`04`, sección 3.1) |
| Existen diferencias visuales reales entre las categorías | **Sin determinar.** Ver la evidencia de abajo |
| Hay suficientes ejemplos de cada categoría | **No, hoy son cero.** Habría que construirlos desde cero |
| Las etiquetas son consistentes | **Sin determinar.** No se encontró una definición normativa colombiana de "criollo" ni de "semicriollo" comparable a la que sí existe para el calibre |

**Evidencia relevante sobre la distinguibilidad visual.** La literatura sobre reconocimiento de
variedades de huevo señala que el aspecto externo de distintas variedades es muy parecido, y por
eso recurre a imagen hiperespectral en el infrarrojo cercano en lugar de cámaras RGB, alcanzando
en torno al 85–86 % de exactitud con ese equipamiento. Por otro lado, existe al menos un conjunto
de datos reciente que sí intenta reconocer variedades a partir de imágenes RGB corrientes. El
detalle y las referencias están en `04-investigacion-datasets.md`, secciones 3.4 y 3.5.

**Interpretación honesta:** no puede concluirse que sea imposible, pero tampoco puede darse por
hecho. Es una pregunta abierta que solo se resuelve con datos propios.

**Una categoría que falta.** Tal como está planteado, el eje solo contempla `criollo` y
`semicriollo`. Si el sistema tuviera que clasificar un huevo comercial de gallina ponedora
—precisamente el tipo de huevo que domina los conjuntos de datos públicos y las bandas
transportadoras reales— no tendría ninguna categoría donde ponerlo. Un eje de clasificación debe
ser **exhaustivo** dentro de su dominio. **Se recomienda añadir una tercera categoría**,
`comercial`, para el huevo de gallina ponedora industrial. Queda como decisión pendiente
(sección 6).

**Relación con el eje A.** Los dos ejes son **independientes**: un huevo criollo puede estar
sucio, y un huevo comercial puede estar agrietado. Dentro de cada eje las categorías sí son
mutuamente excluyentes; entre ejes, no.

**Decisión: eje EXPERIMENTAL.** Se mantiene como requisito del proyecto, pero fuera del MVP.

### 1.3 Eje C — Calibre comercial

**Pregunta que responde:** ¿a qué categoría comercial de tamaño pertenece este huevo?

**Este eje depende de una medición física, no de la apariencia.** El calibre se define por el
**peso en gramos**, y una cámara no pesa. Determinar el calibre a partir únicamente de una
imagen, sin calibración ni información adicional, **no es posible**, por dos razones
encadenadas:

1. **Sin referencia de escala no hay tamaño.** Un huevo pequeño cerca de la cámara ocupa los
   mismos píxeles que uno grande lejos. Para convertir píxeles en milímetros hace falta una
   distancia cámara-objeto fija y conocida, o un patrón de tamaño conocido dentro del cuadro.
2. **Aun teniendo el tamaño, no se tiene el peso.** Pasar de las dimensiones visibles al peso
   exige asumir un modelo de volumen y una densidad. Lo que se obtendría sería una **estimación**
   con error propio, no la medición que la categoría comercial exige.

**De dónde podría venir el peso en una versión futura:**

- de una **balanza o sensor de peso** integrado en la banda, que entregue el valor al sistema;
- de un **valor ingresado manualmente** por el usuario en una demostración;
- de **otro dispositivo o sistema externo** que ya disponga del dato.

En cualquiera de los tres casos, el peso entra al sistema **como una entrada adicional**, no
como una predicción del modelo de visión. La clasificación de calibre sería entonces una simple
comparación del peso contra unos rangos, no un problema de aprendizaje automático.

**Nada de esto se implementa ahora.** No se define hardware, no se elige sensor y no se escribe
código.

**Sobre los rangos exactos.** Este documento **no reproduce la tabla de pesos**. Las cifras
recogidas en `04-investigacion-datasets.md` provienen de fuentes secundarias coincidentes, no del
texto oficial de la NTC 1240, que es una norma de pago del ICONTEC. **Antes de implementar
cualquier regla de calibre habrá que validar los rangos contra la fuente normativa oficial y
citar la edición concreta.**

**Decisión: eje OPCIONAL / FUTURO.**

### 1.4 Resumen de los tres ejes

| | Eje A — Estado | Eje B — Tipo/origen | Eje C — Calibre |
| --- | --- | --- | --- |
| Categorías | bueno, grieta, sucio, danado | criollo, semicriollo (+ comercial, propuesta) | Categorías comerciales por peso |
| Fuente de la información | La imagen | La imagen, si resulta viable | Una medición física externa |
| ¿Observable por cámara? | Sí | Sin determinar | No, por sí sola |
| ¿Hay datos públicos? | Parcialmente | No | No aplica |
| Tipo de problema | Clasificación aprendida | Clasificación aprendida | Comparación contra rangos |
| Prioridad | **OBLIGATORIO** | **EXPERIMENTAL** | **OPCIONAL / FUTURO** |

Un mismo huevo recibe **un valor por cada eje**, no uno solo. Son etiquetas paralelas.

---

## 2. Definición del MVP

*MVP* aquí significa el producto mínimo que hace del trabajo un proyecto completo y defendible:
lo que debe funcionar sí o sí para que el proyecto tenga sentido.

### 2.1 OBLIGATORIO — el MVP

| # | Requisito | Por qué es obligatorio |
| --- | --- | --- |
| 1 | **Detección del huevo** en la imagen, con caja delimitadora y confianza | Sin localizar el huevo no hay nada que clasificar. Es el primer eslabón de todo el flujo |
| 2 | **Clasificación del estado visual** (eje A) | Es la única tarea de clasificación cuya información está completa en la imagen. Es el aporte central del proyecto |
| 3 | **Cámara en tiempo real** | Requisito explícito del proyecto: el usuario no toma fotografías manualmente |
| 4 | **Simulación de banda transportadora** | Es el escenario de uso que da sentido al tiempo real: los huevos pasan, el sistema decide |
| 5 | **Métricas reales del modelo**, medidas sobre una partición de prueba independiente | Sin medición no hay proyecto de ciencia de datos, solo una demostración. Las métricas se reportarán con los valores que se obtengan, sin umbrales prometidos de antemano |

### 2.2 EXPERIMENTAL — se intenta, puede no lograrse

| Requisito | Condición para que entre |
| --- | --- |
| **Clasificación criollo / semicriollo** (eje B) | Que se logre construir un conjunto propio con suficientes ejemplos de cada categoría **y** que el análisis muestre que son visualmente separables |

Se aborda **solo después** de que el MVP funcione. Si el resultado es negativo, **ese resultado
negativo se documenta y se reporta**: demostrar con datos que dos categorías no son separables
visualmente es un hallazgo válido de un trabajo de ciencia de datos, no un fracaso.

### 2.3 OPCIONAL / FUTURO — fuera de esta entrega

| Requisito | Qué requeriría |
| --- | --- |
| **Clasificación por calibre** (eje C) | Una fuente de peso (balanza, sensor, entrada manual o sistema externo) y la validación de los rangos contra la norma oficial |
| Referencia de escala en la escena | Fijar la geometría de captura o incluir un patrón de tamaño conocido |

### 2.4 Por qué esta distribución, según la evidencia

El usuario propuso esta misma distribución. La evidencia recogida en
[`04-investigacion-datasets.md`](04-investigacion-datasets.md) **la confirma**, con dos matices
que conviene dejar escritos porque afectan al trabajo de la siguiente fase:

**Matiz 1: dentro del MVP, la clase `danado` no tiene datos públicos.** Es la clase peor cubierta
de todas: no aparece en ningún conjunto descargable, solo como "broken shell" en conjuntos
privados descritos en artículos. Esto **no la saca del MVP**, porque es la clase más fácil de
generar por captura propia: basta romper deliberadamente algunos huevos y fotografiarlos en
varias orientaciones. Pero significa que **la captura propia es obligatoria desde el principio**,
no un complemento opcional. La clase `sucio` está en una situación parecida aunque menos grave,
con cobertura pública escasa.

**Matiz 2: el eje B está en una situación más débil de lo que sugiere la palabra "experimental".**
No es que existan datos imperfectos: **no existe ningún dato**. Habría que construir el conjunto
completo desde cero, con el agravante de que ni siquiera se encontró una definición normativa de
"criollo" y "semicriollo" que permita etiquetar de forma consistente. A esto se suma la evidencia
de que la literatura recurre a imagen hiperespectral para distinguir variedades.

Ninguno de los dos matices justifica mover un requisito de categoría. **La distribución propuesta
se mantiene tal cual.** El primero refuerza que la captura propia es parte del camino crítico; el
segundo refuerza que el eje B debe permanecer fuera del MVP.

---

## 3. Flujo conceptual del sistema

Así encajan los tres ejes en el procesamiento de cada cuadro de video. Los pasos marcados con
`[MVP]` son los obligatorios; los demás son condicionales.

```
                    Cámara en tiempo real
                             │
                             ▼
                  Detección de huevos          [MVP]
              (caja delimitadora + confianza)
                             │
                             ▼
                 Recorte de cada huevo         [MVP]
                             │
                             ▼
            Clasificación de estado visual     [MVP]
              bueno / grieta / sucio / danado
                             │
                             ▼
         ¿existe un modelo de origen confiable?
                   │                   │
                  sí                   no
                   │                   │
                   ▼                   │
      Clasificación de origen          │        [EXPERIMENTAL]
        criollo / semicriollo          │
                   │                   │
                   └────────┬──────────┘
                            ▼
              ¿hay dato de peso disponible?
                   │                   │
                  sí                   no
                   │                   │
                   ▼                   │
         Clasificación de calibre      │        [FUTURO]
       (comparación contra rangos)     │
                   │                   │
                   └────────┬──────────┘
                            ▼
                      Resultado final
        posición + estado + [origen] + [calibre]
```

**Notas sobre el flujo:**

- Los dos rombos son **condicionales reales, no adornos**. Si no hay modelo de origen fiable o no
  hay dato de peso, el sistema **sigue funcionando** y entrega el resultado con la información
  que tenga. El MVP es la rama por la que se pasa siempre.
- El dato de peso **entra desde fuera**; no lo produce el modelo de visión.
- La clasificación de calibre **no es aprendizaje automático**: es comparar un número contra unos
  rangos.
- El recorte de cada huevo es lo que permite que las clasificaciones trabajen sobre un solo huevo
  aunque el cuadro contenga varios.

---

## 4. Qué no afirma este documento

Para que quede constancia expresa:

- **No se fija ninguna regla de peso.** Los rangos de calibre deberán validarse contra la fuente
  normativa oficial antes de implementarse.
- **No se afirma que el modelo pueda distinguir criollo de semicriollo.** Es una hipótesis por
  comprobar.
- **No se afirma que el calibre pueda inferirse de una imagen.**
- **No se anticipa ninguna métrica, exactitud ni umbral de desempeño.** Se reportará lo que se
  mida.
- **No se declara ninguna definición normativa de "criollo" ni de "semicriollo".** No se encontró
  una fuente colombiana equivalente a la que existe para el calibre; queda como pendiente.
- **No se compromete ninguna arquitectura ni librería de modelado.**

---

## 5. Decisión de alcance

**Alcance actual del proyecto:**

**MVP — obligatorio**

- Detección de huevos en imagen y video.
- Clasificación del estado visual: `bueno`, `grieta`, `sucio`, `danado`.
- Funcionamiento con cámara en tiempo real.
- Simulación de banda transportadora.
- Métricas reales medidas sobre una partición de prueba independiente.

**Experimental**

- Clasificación de origen: `criollo` / `semicriollo`, condicionada a construir un conjunto propio
  y a que las categorías resulten visualmente separables. Un resultado negativo es un resultado
  válido y se documentará.

**Extensión futura**

- Clasificación por calibre comercial, a partir de un peso entregado por una balanza, un sensor,
  una entrada manual o un sistema externo, y con los rangos validados contra la norma oficial.

**Ningún requisito del enunciado original se elimina.** Los tres siguen presentes; lo que cambia
es que ahora están separados en ejes distintos, con una prioridad explícita y con las condiciones
que cada uno necesita para poder abordarse.

---

## 6. Decisiones que quedan abiertas

| # | Decisión | Depende de |
| --- | --- | --- |
| 1 | ¿Se añade `comercial` como tercera categoría del eje B para que sea exhaustivo? | Decisión del equipo (recomendado en la sección 1.2) |
| 2 | Definición operativa de `criollo` y `semicriollo` que permita etiquetar de forma consistente | Encontrar una fuente colombiana; si no existe, acordar una definición propia y documentarla como tal |
| 3 | ¿Un modelo por eje o un modelo multi-salida? | Volumen de datos que se consiga para cada eje |
| 4 | Umbral operativo entre `grieta` y `danado` | Revisión de las imágenes reales que se recolecten |
| 5 | Validación de los rangos de calibre contra el texto oficial de la NTC 1240 | Acceso al documento del ICONTEC |
| 6 | ¿Se monta una referencia de escala en la banda? | Solo si el eje C llega a abordarse |

**Siguiente paso (subpasos 5 y 6 de la Fase 1):** definir los criterios finales de etiquetado con
esta taxonomía ya fijada, y comenzar la recolección de imágenes propias, empezando por la clase
`danado`, que es la que no tiene ninguna cobertura pública.
