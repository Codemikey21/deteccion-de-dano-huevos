/**
 * Intervalo inicial entre capturas automáticas (ms).
 * Valor de partida; no implica frecuencia final de producción.
 */
export const SCAN_INTERVAL_MS = 1000;

/** Timeout por defecto para requests al backend (ms). */
export const API_REQUEST_TIMEOUT_MS = 10_000;

const rawApiUrl = process.env.EXPO_PUBLIC_API_URL?.trim();

/**
 * URL base del backend FastAPI.
 * Debe definirse en mobile/.env como EXPO_PUBLIC_API_URL.
 *
 * En iPhone, `127.0.0.1` apunta al propio teléfono, no al PC de desarrollo.
 */
export const API_BASE_URL = rawApiUrl ? rawApiUrl.replace(/\/$/, '') : '';

export function assertApiBaseUrl(): string {
  if (!API_BASE_URL) {
    throw new Error(
      'EXPO_PUBLIC_API_URL no está configurada. Copia mobile/.env.example a mobile/.env y define la URL del backend.',
    );
  }
  return API_BASE_URL;
}

if (__DEV__) {
  if (API_BASE_URL) {
    console.log('[EggVision] API_BASE_URL:', API_BASE_URL);
  } else {
    console.error(
      '[EggVision] EXPO_PUBLIC_API_URL no está definida. La app no podrá contactar al backend.',
    );
  }
}
