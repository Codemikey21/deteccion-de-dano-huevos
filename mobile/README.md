# Egg Detection — Mobile (Expo)

Base técnica del frontend móvil para detección de huevos con YOLOv8n.

Esta fase **no incluye diseño final** ni integración con AWS. El objetivo es dejar lista la estructura para desarrollo con Expo Go en iPhone.

## Requisitos

- Node.js 18+
- npm
- Expo Go en iPhone
- Backend FastAPI corriendo en el PC (`uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000`)

## Instalación

```bash
cd mobile
npm install
cp .env.example .env
```

Edita `.env` y configura la IP LAN de tu PC:

```env
EXPO_PUBLIC_API_URL=http://192.168.X.X:8000
```

### Importante: 127.0.0.1 no funciona en iPhone

Desde el teléfono, `http://127.0.0.1:8000` apunta al **propio iPhone**, no al PC donde corre FastAPI. Usa la IP local del PC en la misma red Wi-Fi.

## Ejecutar con Expo Go

```bash
npx expo start
```

Escanea el QR con la app **Expo Go** en iPhone. Acepta el permiso de cámara al abrir la pantalla **Scan**.

## Estructura

```
mobile/
├── app/                 # Rutas Expo Router
│   ├── _layout.tsx      # Tabs: Home, Scan, History, Analytics
│   ├── index.tsx        # Home
│   ├── scan.tsx         # Cámara en vivo (base)
│   ├── history.tsx      # Placeholder
│   └── analytics.tsx    # Placeholder
├── src/
│   ├── components/      # UI reutilizable (vacío por ahora)
│   ├── constants/       # SCAN_INTERVAL_MS, API_BASE_URL
│   ├── hooks/           # useAutoScan (preparado, inactivo por defecto)
│   ├── services/        # healthCheck, predictImage
│   ├── types/           # Tipos del backend
│   └── utils/           # mapBboxToPreview
├── assets/
├── .env.example
└── package.json
```

## Pantallas

| Ruta | Descripción |
|------|-------------|
| `/` | Home con enlace a Scan |
| `/scan` | Cámara trasera en vivo; auto-detección preparada pero inactiva |
| `/history` | Placeholder |
| `/analytics` | Placeholder |

## API

El servicio `src/services/api.ts` expone:

- `healthCheck()` → `GET /health`
- `predictImage({ uri })` → `POST /predict`

## Auto-detección (preparada)

- Constante: `SCAN_INTERVAL_MS = 1000`
- Hook: `useAutoScan` evita requests simultáneos
- Por defecto **desactivado** hasta validar el flujo completo con backend real
- En Scan hay un toggle de desarrollo para activar/desactivar el loop

## Limitaciones actuales

- Sin diseño final (Stitch pendiente)
- Sin historial persistente ni analytics real
- Sin dibujo final de bounding boxes en pantalla
- Sin despliegue AWS

## Scripts

```bash
npm start          # Expo dev server
npm run typecheck  # TypeScript sin emitir
```
