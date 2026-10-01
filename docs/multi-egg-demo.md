# EggVision: demo multi-huevo

## Ejecutar localmente

Desde PowerShell, en `C:\Users\Migue\Documents\deteccion-de-daño-huevos`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

En otra terminal, dentro de `mobile`, ejecuta `npm start`. Para usar el servidor
local desde el teléfono, configura `EXPO_PUBLIC_API_URL=http://IP_LAN_DEL_PC:8000`
en `mobile/.env` y reinicia Expo. Teléfono y PC deben estar en la misma red.
No uses localhost en el teléfono. No se cambió tu URL existente ni se desplegó a AWS.

El modo nuevo está activo por defecto. Si deseas ajustar valores, añade las
variables de `backend/.env.example` a `backend/.env`; conserva las demás variables.
Reinicia el backend después de cambiar umbrales. No sobrescribas un .env existente.

## Ensayo antes de presentar

1. Enciende Auto Scan con un huevo. La primera inferencia es más lenta: deja
   completar una captura antes de presentar.
2. Prueba la mesa vacía: debe mostrar cero huevos, sin conservar el conteo previo.
3. Coloca un huevo claro sano; después uno con una raya oscura alargada en el centro.
4. Coloca cinco objetos separados y bien iluminados, primero todos sanos y después
   mezclados. Verifica cada estado y que sanos + dañados = total.
5. Confirma el conteo con los objetos reales. El complemento de forma recupera
   huevos marrones sobre fondos neutros; las pelotas blancas siguen dependiendo
   de YOLO. Usa un fondo liso y evita objetos marrones que no sean huevos.
6. Revisa “ciclo completo” en Scan: incluye captura, preparación, red e inferencia;
   se suma además la pausa configurada entre ciclos.

La lista se numera de izquierda a derecha en la imagen enviada; con igual centro
horizontal se usa la posición vertical. Los números pertenecen a esa captura,
pueden cambiar y no son identidades persistentes. La orientación de la imagen
enviada puede diferir de la vista previa. No se dibujan cajas multi-huevo sobre
la cámara mientras no esté verificada su correspondencia.

## Configuración

| Variable del backend | Valor inicial | Efecto |
| --- | --- | --- |
| ENABLE_MULTI_EGG | true | false restaura el flujo anterior single-egg |
| EGG_CONFIDENCE | 0.40 | Confianza mínima para contar un huevo |
| CRACK_CONFIDENCE | 0.55 | Confianza mínima de grieta YOLO para marcar daño |
| DAMAGE_DARK_THRESHOLD | 100 | Límite de gris oscuro, 0–255; subir admite marcas más claras |
| DAMAGE_MIN_CONTRAST | 35 | Contraste mínimo respecto a la iluminación local estimada |
| DAMAGE_MIN_AREA_RATIO | 0.003 | Fracción mínima del interior ocupada por una marca conectada |
| DAMAGE_MIN_LENGTH_RATIO | 0.18 | Largo mínimo relativo al lado menor del recorte |
| DAMAGE_MIN_ELONGATION | 2.5 | Relación largo/ancho mínima de la marca |
| DAMAGE_INNER_SCALE | 0.80 | Elipse interior; excluye bordes/fondo, pero pierde marcas en el borde |
| DAMAGE_ROI_MAX_SIDE | 256 | Lado máximo del recorte analizado por OpenCV |

Empieza con iluminación uniforme, objetos claros, separados, sin logos y una raya
central visible. Si no detecta una raya gris, sube DARK_THRESHOLD ligeramente.
Si pequeñas manchas se clasifican como daño, sube MIN_AREA_RATIO o MIN_LENGTH_RATIO.
No bajes umbrales a ciegas: comprueba de nuevo un objeto sano y la mesa vacía.
`MODEL_CONFIDENCE` no debe superar `EGG_CONFIDENCE` ni `CRACK_CONFIDENCE`, porque
YOLO descarta esas detecciones antes del análisis posterior.

En `mobile/.env`, `EXPO_PUBLIC_SCAN_INTERVAL_MS=150` configura la pausa entre
ciclos completos (mínimo 100 ms). Antes era 1000 ms. Sigue habiendo una sola
petición en curso. No equivale a 150 ms de latencia total.

## Contrato y compatibilidad

- Una inferencia YOLO de la imagen completa a 960; ninguna segunda inferencia
  YOLO en modo multi, incluso con un único huevo.
- `eggs[]`: `id`, `bbox`, `bbox_normalized`, `confidence` de YOLO (0 cuando el
  objeto solo viene de la heurística), `localization_source`, `status`
  (`healthy`/`damaged`), `damage_source`, `dark_line_area_ratio` y `cracks`.
  La fracción de marca no es una probabilidad ni confianza de una red.
- `summary`: `total`, `healthy`, `damaged`, para toda la captura.
- `timing`: `full_frame_ms`, `roi_analysis_ms`, `total_ms` (decodificación,
  inferencia y análisis; no incluye captura ni red del móvil).
- Los campos anteriores siguen presentes. `primary_egg` es el huevo de mayor
  confianza del grupo; `status`, `route`, `reason`, `egg_detected`, `crack_detected`
  y `cracks` describen ese huevo, NO el grupo entero. Una raya puede activar
  `crack_detected` por compatibilidad; consulta `damage_source` para distinguirla
  de una grieta YOLO. No se inventan detecciones YOLO de grieta para las rayas.
- `inference_ms`, `full_frame_inference_ms` y `total_inference_ms` mantienen
  significado de tiempo YOLO. El trabajo clásico adicional aparece en `timing`.
- Con `ENABLE_MULTI_EGG=false`, se conserva la selección y segunda pasada ROI
  anteriores (según `ENABLE_EGG_ROI_INFERENCE`). `eggs`, `summary`, `timing` son null
  y Scan utiliza su presentación y registro anteriores.
- El modo multi muestra resultados por captura, sin persistir inspecciones en
  el historial single-egg: no hay seguimiento de identidades entre capturas y
  guardarlas como un solo huevo falsearía los conteos históricos.

## Límites de la demo

“Sano” significa que no se encontró evidencia visible con estos umbrales. No es
una garantía de integridad física. Rayas impresas, logos y sombras pueden causar
falsos positivos; rayas finas, curvas, borrosas o cerca del borde pueden perderse.
El modelo existente puede no reconocer huevos plásticos o pelotas de ping pong.
No se entrenó, sustituyó ni modificó `best.pt`. Falta validar los objetos reales
de la demo y la cámara del teléfono. Fotos/vídeos cargados como funciones nuevas
no forman parte de este cambio: se mantiene Auto Scan y el POST de imagen existente.

## Corrección de omisiones y sombras

Las escenas de la demo mostraron que YOLO omite incluso huevos grandes, y
que el umbral oscuro global podía interpretar una sombra como daño. Ahora:

- `demo_localization.py` complementa YOLO con segmentación de tonos marrones,
  filtrado por forma, centros de distancia y separación de objetos en contacto.
  Normaliza la escala y adapta el corte de brillo a la exposición.
- Combina las cajas de ambos métodos sin duplicar el mismo huevo. Si una caja
  YOLO agrupa varias formas, utiliza las formas separadas.
- El análisis de marcas usa contraste local y rechaza componentes pegados al
  borde interior, para reducir falsos positivos de sombras y uniones entre huevos.
  También acepta marcas irregulares amplias, como el garabato de la demostración.
- `localization_source` indica `yolo`, `demo_shape` o `yolo+demo_shape`.
  `confidence=0` en `demo_shape` significa ausencia de puntuación YOLO;
  no es una probabilidad inventada para la heurística.
- Las roturas físicas claras siguen usando las detecciones de grieta del modelo.
  El frontend dice “marca oscura visible” para la evidencia clásica, sin asegurar
  que toda marca sea una simulación dibujada.

Variables nuevas, con defaults activos tras reiniciar el backend:

| Variable | Default | Efecto |
| --- | --- | --- |
| ENABLE_DEMO_LOCALIZATION | true | Complemento para huevos marrones; false lo desactiva |
| DEMO_MIN_SATURATION | 65 | Saturación mínima del tono marrón |
| DEMO_MIN_VALUE | 65 | Corte de brillo base, ajustado por exposición |
| DEMO_MIN_AREA_RATIO | 0.003 | Área mínima relativa al frame |
| DEMO_MAX_AREA_RATIO | 0.45 | Rechaza regiones marrones excesivamente grandes |
| DEMO_MAX_SIDE | 640 | Resolución de trabajo normalizada del complemento |
| DEMO_MAX_OBJECTS | 32 | Máximo de candidatos por forma |
| DAMAGE_LOCAL_WINDOW_RATIO | 0.25 | Ventana de iluminación relativa al recorte |
| DAMAGE_MARK_AREA_RATIO | 0.015 | Área mínima para una marca irregular no alargada |

Este complemento es específico para la demo: puede confundir otros objetos
marrones ovalados y no añade reconocimiento general de huevos blancos o pelotas.
Mantiene una sola llamada a YOLO. No se cambia el checkpoint ni se entrena.

Validación de la corrección: 116 tests backend, incluidos los nueve recortes
reales, con escala 0.65 y brillo 0.8/1.2, fondos vacíos, ruido y deduplicación.
Con el modelo real y confianza 0.25, los nueve recortes originales dan los
conteos esperados (4,1,1,2,2,2,4,4,4), cada uno con un dañado visible.
Esto verifica las capturas suministradas, no garantiza precisión general ni
latencia de cámara/red. Se debe repetir la prueba física después del despliegue.

## Comprobaciones de la primera versión

- Backend: `python -m pytest backend/tests -q`: 64 passed; dos avisos de
  deprecación de dependencias TestClient.
- Mobile: `npm test`: 33 passed. `npm run typecheck`: sin errores.
- Lint se ejecutó y encontró dos errores anteriores a este cambio:
  `useAutoScan.ts:82` (react-hooks/refs) y `useEggVision.ts:88`
  (react-hooks/set-state-in-effect). El repo no tenía configuración ESLint;
  se retiraron la configuración y cambios de manifests generados automáticamente
  por Expo. No se refactorizaron esos hooks dentro del alcance de la demo.
- Pruebas nuevas: cero huevos, sano, raya, cinco huevos mezclados, orden,
  resumen, orientación de rayas, manchas/ruido, umbrales, asociación única de
  grietas, cajas inválidas y regreso al flujo antiguo. Tests del endpoint
  verifican exactamente una llamada YOLO y cero llamadas ROI en modo multi.
- Smoke real sobre `IMG_20220817_155821.jpg`: un huevo sano detectado. Primera
  inferencia: 4425 ms; segunda: 214 ms YOLO + 20 ms análisis ROI, 301 ms local
  incluyendo decodificación. Es una muestra, no un benchmark del teléfono.

## Revisar sin commits

Desde la raíz puedes ejecutar `git diff --stat`, `git diff` y `git status --short`.
Los archivos nuevos aparecen con `??` y no salen en `git diff` hasta que se
incluyan en el índice; se revisan abriéndolos. Revisa siempre los archivos incluidos antes de crear el commit.
La carpeta `.claude/` ya estaba sin seguimiento antes de comenzar y no se modificó.
