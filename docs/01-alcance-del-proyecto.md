# Alcance del proyecto

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Estado del documento: versión inicial (Fase 0)

---

## 1. Problema

El proyecto aborda el problema académico de automatizar, mediante visión artificial, la
identificación visual del estado de los huevos en un escenario simulado de clasificación.

La inspección visual de un huevo es una tarea de reconocimiento de patrones sobre imágenes, lo
que la convierte en un caso de estudio apropiado para las técnicas de la asignatura.

Este documento **no afirma** cifras, conclusiones ni comparaciones sobre cómo se realiza hoy
la inspección de huevos en la industria. Cualquier justificación de ese tipo se incorporará
más adelante únicamente si se respalda con referencias verificables.

## 2. Propuesta

Un sistema de visión artificial que observe los huevos a través de una cámara mientras pasan
frente a ella, simulando una banda transportadora, y que los detecte y clasifique de forma
automática. La captura es continua: el usuario **no** toma fotografías manualmente.

## 3. Tareas de aprendizaje

El sistema combina dos tareas sobre cada huevo detectado en el cuadro de video:

**a) Clasificación por estado**

| Clase | Descripción |
| --- | --- |
| Bueno | Cáscara íntegra y limpia |
| Grieta | Fisura visible sin pérdida de contenido |
| Sucio | Cáscara íntegra con suciedad adherida |
| Dañado | Cáscara rota o deformada |

**b) Clasificación por tipo — definición pendiente de validación**

La clasificación por tipo es un **requisito propuesto del proyecto** y se mantiene dentro del
alcance. Sin embargo, las categorías del enunciado todavía **no tienen una definición
operativa** y **no deben asumirse como tres clases mutuamente excluyentes**.

| Categoría propuesta | Estado de la definición |
| --- | --- |
| Triple A | Por validar. Investigar si corresponde a una característica de calibre o tamaño. |
| Criollo | Por validar. Investigar si corresponde a una característica de origen o tipo de producción. |
| Semicriollo | Por validar. Investigar su definición y su relación con las dos anteriores. |

Antes de etiquetar el conjunto de datos deben resolverse estos puntos:

1. **Verificar con fuentes** la definición de cada categoría y determinar si pertenecen al
   mismo eje de clasificación. Si "Triple A" describe calibre mientras que "criollo" y
   "semicriollo" describen origen, se trata de dos atributos distintos y no de tres clases
   excluyentes.
2. **Comprobar qué es distinguible en las imágenes** que efectivamente se logren recolectar.
   Una categoría que no sea separable visualmente no puede sostenerse como clase.
3. **No asumir que la cámara puede determinar el calibre real.** Estimar el tamaño físico a
   partir de una imagen exige una referencia de escala conocida: distancia cámara-objeto fija,
   un patrón de tamaño conocido en la escena, o información adicional externa.

Según el resultado de esa investigación, la solución podrá implementarse como una
clasificación única, como predicción de atributos múltiples o como modelos separados. La
decisión se documentará aquí cuando se tome.

## 4. Entradas y salidas

- **Entrada:** flujo de video en vivo de una cámara (webcam o cámara IP).
- **Salida:** por cada huevo detectado, su posición en el cuadro, la clase de estado y la
  información de tipo según la definición que se valide en la sección 3b, junto con la
  confianza del modelo.

## 5. Dentro del alcance

- Construcción de un conjunto de datos propio de imágenes de huevos.
- Investigación y definición operativa de las categorías de tipo (sección 3b).
- Etiquetado del conjunto de datos por estado y por tipo.
- Entrenamiento y evaluación de un modelo de detección y clasificación.
- Inferencia sobre video en tiempo real.
- Interfaz web que muestre el video procesado y el resultado de la clasificación.
- Despliegue en una instancia EC2 de AWS Academy Learner Lab.

## 6. Fuera del alcance

- Control físico de una banda transportadora real (se simula el paso de los huevos).
- Detección de defectos internos del huevo (requeriría ovoscopía u otro tipo de sensor).
- Estimación de peso o medidas físicas exactas.
- Autenticación de usuarios y gestión de roles.
- Operación permanente en producción: el Learner Lab tiene sesiones con tiempo limitado.

## 7. Restricciones conocidas

- **AWS Academy Learner Lab:** presupuesto en créditos limitado y las instancias se detienen
  al cerrar la sesión del laboratorio. El despliegue debe poder recrearse rápidamente.
- **Conjunto de datos propio:** no se parte de un dataset público, por lo que el volumen de
  imágenes dependerá del tiempo de captura y etiquetado disponible.
- **Tiempo real:** la inferencia debe ser suficientemente rápida sobre video; el tamaño del
  modelo está condicionado por el hardware disponible.
- **Calibre y referencia de escala:** una imagen por sí sola no permite determinar el tamaño
  físico real de un huevo. Cualquier categoría basada en calibre exigiría fijar la geometría
  de la captura o incluir un patrón de referencia en la escena.

## 8. Decisiones pendientes

Se resolverán en la fase correspondiente y se documentarán aquí:

1. **Definición de las categorías de tipo** (sección 3b): a qué eje pertenece cada una y si
   son excluyentes entre sí. Es la decisión de la que dependen las demás.
2. **Estrategia de etiquetas**, condicionada por la anterior: clasificación única,
   predicción de atributos múltiples o modelos separados para estado y para tipo.
3. **Arquitectura y librería del modelo**: detector de objetos de una etapa frente a
   detección con OpenCV seguida de un clasificador sobre el recorte de cada huevo. No se
   compromete de antemano ninguna librería ni arquitectura concreta.
4. **Origen de las imágenes**: captura propia, imágenes cedidas o una combinación.
5. **Geometría de la captura**: si se fija la distancia cámara-objeto o se incluye un patrón
   de referencia, necesario únicamente si alguna categoría depende del calibre.
6. **Infraestructura**: tipo de instancia EC2 y si la inferencia se ejecutará en la nube o en
   el equipo local con la nube sirviendo únicamente la aplicación web.

## 9. Criterios de éxito

El proyecto se considerará exitoso si:

1. El sistema detecta huevos en video en vivo sin intervención manual del usuario.
2. Entrega una clasificación de estado por cada huevo detectado y, según la definición que se
   valide en la sección 3b, la información de tipo.
3. El desempeño del modelo se reporta con métricas medidas sobre un conjunto de prueba
   independiente. Los umbrales se definirán al conocer el tamaño y el balance reales del
   conjunto de datos; no se fija ningún valor por anticipado.
4. La solución queda desplegada y accesible desde el navegador.
