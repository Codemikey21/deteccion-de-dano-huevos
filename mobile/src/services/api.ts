import { API_REQUEST_TIMEOUT_MS, assertApiBaseUrl } from '../constants/config';
import type { HealthResponse, PredictionResponse } from '../types/prediction';

interface ErrorResponseBody {
  detail?: string;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function logDevSuccess(label: string): void {
  if (__DEV__) {
    console.log(`[EggVision] ${label}`);
  }
}

function logDevError(label: string, error: unknown): void {
  if (__DEV__) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`[EggVision] ${label}:`, message);
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number = API_REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(`Timeout tras ${timeoutMs}ms`, 0);
    }

    throw new ApiError(
      error instanceof Error ? error.message : 'Error de red al contactar el backend',
      0,
    );
  } finally {
    clearTimeout(timer);
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    throw new ApiError('Respuesta vacía del servidor', response.status);
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError('Respuesta JSON inválida del servidor', response.status);
  }
}

export async function healthCheck(): Promise<HealthResponse> {
  const baseUrl = assertApiBaseUrl();

  try {
    const response = await fetchWithTimeout(`${baseUrl}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });

    if (!response.ok) {
      throw new ApiError(`Health check failed (${response.status})`, response.status);
    }

    const data = await parseJson<HealthResponse>(response);
    logDevSuccess(
      `health ok · model_loaded=${data.model_loaded} · model=${data.model} · input_size=${data.input_size}`,
    );
    return data;
  } catch (error) {
    logDevError('health error', error);
    throw error;
  }
}

export interface PredictImageInput {
  uri: string;
  mimeType?: 'image/jpeg' | 'image/png';
  fileName?: string;
}

export async function predictImage(input: PredictImageInput): Promise<PredictionResponse> {
  const baseUrl = assertApiBaseUrl();
  const mimeType = input.mimeType ?? 'image/jpeg';
  const fileName = input.fileName ?? 'frame.jpg';

  const formData = new FormData();
  formData.append('file', {
    uri: input.uri,
    type: mimeType,
    name: fileName,
  } as unknown as Blob);

  try {
    const response = await fetchWithTimeout(`${baseUrl}/predict`, {
      method: 'POST',
      body: formData,
      headers: { Accept: 'application/json' },
    });

    if (!response.ok) {
      const detail = await readPredictErrorDetail(response);
      throw new ApiError(detail, response.status);
    }

    const data = await parseJson<PredictionResponse>(response);
    logDevSuccess(`predict ok · status=${data.status} · detections=${data.detections.length}`);
    return data;
  } catch (error) {
    logDevError('predict error', error);
    throw error;
  }
}

async function readPredictErrorDetail(response: Response): Promise<string> {
  const fallback = `Predict failed (${response.status})`;

  try {
    const body = (await response.json()) as ErrorResponseBody;
    return body.detail ?? fallback;
  } catch {
    return fallback;
  }
}
