# Datos

**El contenido de esta carpeta no se versiona en Git.** Solo se conservan este archivo y los
`.gitkeep` que mantienen la estructura de directorios. Las imágenes pesan demasiado para un
repositorio Git y el conjunto de datos se reconstruye desde su fuente original.

> A la fecha no existe todavía ningún dato en el proyecto. Las carpetas están vacías a
> propósito; se llenarán en la fase de construcción del conjunto de datos.

## Organización

| Carpeta | Contenido |
| --- | --- |
| `raw/` | Imágenes tal como se capturaron, sin modificar. Nunca se editan ni se borran: son la fuente de verdad. |
| `processed/` | Imágenes derivadas de `raw/` tras redimensionar, recortar o normalizar. Se pueden regenerar en cualquier momento. |

Las particiones `train/`, `validation/` y `test/` se crearán al exportar el conjunto de datos
etiquetado, en la fase correspondiente.

## Convención de nombres

Se definirá al iniciar la captura de imágenes y se documentará aquí, junto con el origen de
cada lote de imágenes y la fecha de captura.
