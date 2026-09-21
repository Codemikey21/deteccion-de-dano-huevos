# Detección y clasificación de huevos mediante visión artificial

Proyecto de la asignatura **Ciencia de Datos** — Ingeniería de Sistemas.

> **Estado actual: Fase 0 — preparación del repositorio.**
>
> A la fecha **no existe conjunto de datos**, **no existe modelo entrenado** y **no existe
> aplicación funcional**. Este repositorio contiene únicamente la estructura base y la
> documentación del alcance. Todo lo descrito más abajo es planificación, no funcionalidad
> ya implementada.

---

## 1. Descripción

Sistema de visión artificial que detecta huevos a través de una cámara **en tiempo real**
—simulando una banda transportadora— y los clasifica automáticamente, sin que el usuario
tenga que capturar fotografías de forma manual.

Por cada huevo detectado se busca determinar dos atributos:

| Atributo | Categorías propuestas |
| --- | --- |
| Estado | Bueno · Grieta · Sucio · Dañado |
| Tipo | Triple A · Criollo · Semicriollo |

La clasificación por **tipo** es un requisito propuesto del proyecto y se mantiene dentro del
alcance, pero la definición final de sus categorías está **pendiente de validación**: debe
investigarse si "Triple A" corresponde a una característica de calibre o tamaño mientras que
"criollo" y "semicriollo" corresponden a una característica de origen o tipo de producción.
De esa investigación dependerá si se resuelve con una clasificación única, con atributos
múltiples o con modelos separados. El detalle está en
[`docs/01-alcance-del-proyecto.md`](docs/01-alcance-del-proyecto.md).

## 2. Objetivos

**Objetivo general**

Desarrollar un sistema de visión artificial capaz de detectar y clasificar huevos en tiempo
real a partir del flujo de video de una cámara.

**Objetivos específicos**

1. Construir un conjunto de datos propio de imágenes de huevos, etiquetado por estado y por tipo.
2. Entrenar y evaluar un modelo de detección y clasificación sobre ese conjunto de datos.
3. Implementar la inferencia sobre video en vivo, con detección automática de cada huevo.
4. Exponer el sistema mediante una API FastAPI consumida por una aplicación móvil React Native + Expo + TypeScript (en desarrollo, acceso desde iPhone mediante Expo Go).
5. Desplegar el servicio de inferencia en una instancia EC2 de AWS Academy Learner Lab.

El detalle del alcance está en [`docs/01-alcance-del-proyecto.md`](docs/01-alcance-del-proyecto.md)
y el plan por fases en [`docs/02-plan-de-trabajo.md`](docs/02-plan-de-trabajo.md).

## 3. Tecnologías consideradas

Se incorporan **a medida que cada fase las necesita**, no todas desde el inicio. Las marcadas
como *candidata* todavía no están decididas.

| Área | Herramientas | Estado |
| --- | --- | --- |
| Lenguaje | Python 3.11 | Confirmada |
| Visión por computador | OpenCV | Confirmada |
| Manejo de datos | NumPy | Confirmada |
| Control de versiones | Git, GitHub | Confirmada |
| Infraestructura | AWS EC2 (Academy Learner Lab) | Confirmada |
| Entrenamiento | Google Colab con GPU | Confirmada (no ejecutado) |
| Detector | YOLOv8 (seleccionado provisionalmente); baseline **YOLOv8n**; comparación posterior **YOLOv8s** | Decisión técnica provisional (no entrenado, no validado) |
| Backend | FastAPI | Confirmada (no implementado) |
| Frontend | React Native + Expo + TypeScript; acceso desde iPhone mediante Expo Go durante el desarrollo | Confirmada (no implementado) |
| Cámara (desarrollo) | expo-camera | Confirmada (no implementado) |
| Animaciones | React Native Reanimated | Confirmada (no implementado) |
| Etiquetado del conjunto de datos | Roboflow | Candidata |
| Análisis exploratorio | Pandas, Matplotlib | Candidata |
| Clasificador de estado | Arquitectura todavía por definir | Pendiente |

La arquitectura es **modular**: detector de huevos, clasificador de estado visual y
extensiones posteriores. El detalle está en
[`docs/10-decision-tecnica-provisional.md`](docs/10-decision-tecnica-provisional.md).
**No hay modelo entrenado.** El conjunto `egg_dataset` de Ahmed Raza es
**CANDIDATO TÉCNICO PRINCIPAL — PENDIENTE DE LICENCIA**: no está aprobado ni descargado.

## 4. Estructura del repositorio

Estructura **actual** (Fase 0):

```
deteccion-de-dano-huevos/
├── data/                 # Conjuntos de datos (contenido no versionado)
│   ├── raw/              # Imágenes originales sin procesar
│   ├── processed/        # Imágenes ya preparadas
│   └── README.md
├── docs/                 # Documentación del proyecto
│   ├── 01-alcance-del-proyecto.md
│   └── 02-plan-de-trabajo.md
├── .env.example          # Plantilla de variables de entorno
├── .gitattributes        # Normalización de finales de línea
├── .gitignore            # Archivos excluidos del control de versiones
├── README.md
└── requirements.txt      # Dependencias de la fase actual
```

Estructura **objetivo**, al finalizar todas las fases:

```
deteccion-de-dano-huevos/
├── data/              # Conjuntos de datos (contenido no versionado)
│   ├── raw/           # Imágenes originales tal como se capturaron
│   ├── processed/     # Imágenes ya preparadas
│   ├── train/         # Partición de entrenamiento
│   ├── validation/    # Partición de validación
│   └── test/          # Partición de prueba
├── notebooks/         # Análisis exploratorio
├── training/          # Scripts de entrenamiento
├── models/            # Modelos entrenados (contenido no versionado)
├── evaluation/        # Métricas y análisis de resultados
├── src/               # Módulos de inferencia y procesamiento en tiempo real
├── backend/           # API
├── frontend/          # Aplicación React Native + Expo + TypeScript
├── scripts/           # Utilidades de apoyo
├── tests/             # Pruebas automatizadas
├── deploy/            # Configuración y documentación de despliegue
└── docs/              # Documentación
```

Las carpetas que aún no existen se crearán en el commit de la fase que las estrene, para que
el historial refleje el avance real del trabajo. La fase que corresponde a cada una está
indicada en [`docs/02-plan-de-trabajo.md`](docs/02-plan-de-trabajo.md).

## 5. Puesta en marcha

Requiere Python 3.11.

```powershell
# 1. Crear y activar el entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar las dependencias de la fase actual
pip install -r requirements.txt

# 3. Crear la configuración local a partir de la plantilla
Copy-Item .env.example .env
```

El archivo `.env` es local y nunca se sube al repositorio.

## 6. Autor

**Miguel Ángel Solano Díaz**
Universidad Autónoma de Bucaramanga
Asignatura: Ciencia de Datos — Ingeniería de Sistemas
