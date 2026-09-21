# Decisión técnica provisional

Asignatura: Ciencia de Datos — Ingeniería de Sistemas
Fecha: 21 de septiembre de 2026
Documentos relacionados: [`05-taxonomia-clasificacion.md`](05-taxonomia-clasificacion.md) ·
[`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md) ·
[`01-alcance-del-proyecto.md`](01-alcance-del-proyecto.md)

> **No se ha entrenado ningún modelo.** No se ha descargado el conjunto `egg_dataset` de Ahmed
> Raza. Esta decisión es de arquitectura y de herramientas; no autoriza entrenamiento ni
> descarga.

---

## 1. Alcance de esta decisión

Queda fijada, de forma **provisional**, la pila con la que se implementará el MVP:

- detector de huevos;
- dónde se entrena;
- cómo se sirve la inferencia;
- con qué cliente se muestra el resultado.

Sigue abierta la licencia de `egg_dataset`. El recuento académico quedó resuelto: posteriormente,
el profesor confirmó que un conjunto de al menos 800 imágenes es aceptable. Por tanto, INDIGO
con 840 imágenes cumple el requisito académico y es el dataset principal inicial. **No se
entrena hasta descargar e inspeccionar INDIGO.**

---

## 2. Arquitectura modular

El sistema se parte en módulos independientes. Cada uno puede entrenarse, evaluarse y
reemplazarse sin rehacer los demás.

```
1. Detector de huevos          [MVP]
   Entrada: cuadro de video
   Salida:  cajas + confianza, clase única `egg`

2. Clasificador de estado      [MVP]
   Entrada: recorte de cada huevo
   Salida:  bueno | grieta | sucio | danado

3. Extensiones posteriores     [no MVP]
   origen (criollo / semicriollo)     — experimental
   calibre (peso externo)             — futuro
```

Este recorte coincide con el flujo de
[`05-taxonomia-clasificacion.md`](05-taxonomia-clasificacion.md), sección 3. El detector no
predice el estado; el clasificador no localiza huevos.

**No se implementan todavía** los módulos 1–3. Solo se declara la separación.

---

## 3. Detector: YOLOv8

**Detector seleccionado de forma provisional: YOLOv8.** Es una decisión técnica provisional:
**no está entrenado ni validado.**

| Papel | Variante | Cuándo |
| --- | --- | --- |
| Baseline inicial | **YOLOv8n** (nano) | Primera corrida, después de descargar e inspeccionar INDIGO (840 imágenes; cumple el umbral de 800) |
| Comparación futura | **YOLOv8s** (small) | Después, si hay GPU y tiempo |

YOLOv8n se elige como baseline porque es la variante más ligera de la familia: cabe en Colab
y, más adelante, en una instancia EC2 de Learner Lab. YOLOv8s queda como contraste de
capacidad, no como compromiso de partida.

Esta decisión cubre **solo el detector** (módulo 1). El clasificador de estado (módulo 2)
sigue **pendiente**: se elegirá cuando existan recortes etiquetados suficientes. No se afirma
aquí EfficientNet, ResNet ni ninguna otra red de clasificación.

**No se entrena en este paso.** No se añaden pesos ni `ultralytics` a `requirements.txt` hasta
la fase de entrenamiento.

---

## 4. Conjunto de datos del detector

`egg_dataset` de Ahmed Raza (Ultralytics Platform, 2.553 imágenes declaradas,
https://platform.ultralytics.com/ahmed-raza/datasets/eggdataset) queda así:

```
CANDIDATO TÉCNICO PRINCIPAL — PENDIENTE DE LICENCIA.
```

`egg_dataset` **no está aprobado.** La ficha no muestra licencia. No se descarga. No se usa
para entrenar.

El dataset **principal inicial** es INDIGO (840, CC BY 4.0). Posteriormente, el profesor
confirmó que un conjunto de al menos 800 imágenes es aceptable; INDIGO cumple ese umbral. Ver
[`09-revision-datasets-requisito-1000.md`](09-revision-datasets-requisito-1000.md), sección 12.
Egg-Detection (51, MIT) sigue como complementario.

---

## 5. Entrenamiento e inferencia

| Etapa | Dónde | Estado |
| --- | --- | --- |
| Entrenamiento | **Google Colab con GPU** | Decidido; no ejecutado |
| Inferencia (servicio) | **FastAPI** | Decidido; no implementado |
| Inferencia (despliegue) | **AWS EC2** (Academy Learner Lab) | Decidido; no configurado |
| Cliente | **React Native + Expo + TypeScript** | Decidido; no implementado |
| Desarrollo | **Expo Go** en iPhone | Decidido; no implementado |
| Cámara | **expo-camera** | Decidido; no implementado |
| Animaciones | **React Native Reanimated** | Decidido; no implementado |

El entrenamiento en Colab se usará para no saturar el equipo local ni los créditos de Learner
Lab durante las corridas largas. Los pesos resultantes se guardarán en `models/` (fuera de
Git) y la API de FastAPI los cargará para inferir. EC2 hospeda ese servicio; no es el lugar
previsto para entrenar.

El cliente del MVP será una aplicación móvil **React Native + Expo + TypeScript**. Durante el
desarrollo se abre con **Expo Go** en iPhone. La cámara usa **expo-camera**; las animaciones,
**React Native Reanimated**. Eso no cambia el alcance de detección en tiempo real: cambia el
cliente. No es una interfaz web ni una página HTML/CSS/JavaScript.

Ninguna de estas piezas existe todavía en el repositorio.

---

## 6. Qué no queda decidido

- Licencia y uso de `egg_dataset` (Ahmed Raza).
- Arquitectura concreta del **clasificador de estado**.
- Versión exacta del paquete `ultralytics` (se fijará al instalar, en la fase de
  entrenamiento).
- Tipo de instancia EC2.

---

## 7. Decisión resumida

```
DETECTOR:
    Selección provisional: YOLOv8   (no entrenado, no validado)
    Baseline:    YOLOv8n
    Comparación futura: YOLOv8s, si los recursos lo permiten

DATOS DEL DETECTOR:
    egg_dataset (Ahmed Raza):
        CANDIDATO TÉCNICO PRINCIPAL — PENDIENTE DE LICENCIA
        no aprobado, no descargado

ARQUITECTURA:
    1. detector de huevos
    2. clasificador de estado visual   (arquitectura pendiente)
    3. extensiones posteriores

ENTRENAMIENTO:
    Google Colab con GPU     (no ejecutado)

INFERENCIA:
    FastAPI  →  AWS EC2 (Academy Learner Lab)   (no implementado)

CLIENTE:
    React Native + Expo + TypeScript
    Desarrollo: Expo Go en iPhone
    Cámara: expo-camera
    Animaciones: React Native Reanimated
    (no implementado)
```

**Siguiente paso técnico:** no entrenar. Descargar e inspeccionar INDIGO
(`scripts/download_indigo_dataset.py`). `egg_dataset` sigue pendiente de licencia y no cubre
cantidad.
