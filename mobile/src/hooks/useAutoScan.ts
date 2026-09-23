import { CameraView } from 'expo-camera';
import {
  Dispatch,
  RefObject,
  SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

import { SCAN_INTERVAL_MS } from '../constants/config';
import { predictImage } from '../services/api';
import type { PredictionResponse } from '../types/prediction';
import { preprocessCapture } from '../utils/imagePreprocess';

export interface ScanMetrics {
  captureMs: number;
  preprocessMs: number;
  uploadNetworkMs: number;
  serverInferenceMs: number;
  cycleMs: number;
  resized: boolean;
}

export interface UseAutoScanOptions {
  cameraRef: RefObject<CameraView | null>;
  cameraReady: boolean;
  enabled?: boolean;
  intervalMs?: number;
}

export interface UseAutoScanResult {
  autoScanEnabled: boolean;
  setAutoScanEnabled: Dispatch<SetStateAction<boolean>>;
  isProcessing: boolean;
  prediction: PredictionResponse | null;
  error: string | null;
  lastInferenceMs: number | null;
  metrics: ScanMetrics | null;
}

const CAMERA_CAPTURE_BACKOFF_MS = 2000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isCameraCaptureError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return (
    message.includes('Image could not be captured') ||
    message.includes('CameraImageCaptureException')
  );
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Error de inferencia';
}

/**
 * Auto-detección periódica: captura → preprocess → POST /predict → actualiza estado.
 * Un solo request in-flight; el intervalo corre entre ciclos completos.
 */
export function useAutoScan({
  cameraRef,
  cameraReady,
  enabled: enabledProp = false,
  intervalMs = SCAN_INTERVAL_MS,
}: UseAutoScanOptions): UseAutoScanResult {
  const [autoScanEnabled, setAutoScanEnabled] = useState(enabledProp);
  const [isProcessing, setIsProcessing] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastInferenceMs, setLastInferenceMs] = useState<number | null>(null);
  const [metrics, setMetrics] = useState<ScanMetrics | null>(null);

  const inFlightRef = useRef(false);
  const mountedRef = useRef(true);
  const enabledRef = useRef(autoScanEnabled);
  const lastLoggedErrorRef = useRef<string | null>(null);
  enabledRef.current = autoScanEnabled;

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const logCycleWarning = useCallback((message: string) => {
    if (typeof __DEV__ === 'undefined' || !__DEV__ || lastLoggedErrorRef.current === message) {
      return;
    }
    lastLoggedErrorRef.current = message;
    console.warn('[EggVision] cycle error:', message);
  }, []);

  const runCycle = useCallback(async (): Promise<number> => {
    if (inFlightRef.current || !cameraReady) {
      return intervalMs;
    }

    const camera = cameraRef.current;
    if (!camera) {
      const message = 'CameraView no está lista';
      if (mountedRef.current) {
        setError(message);
      }
      logCycleWarning(message);
      return intervalMs;
    }

    inFlightRef.current = true;
    if (mountedRef.current) {
      setIsProcessing(true);
    }

    const cycleStart = Date.now();
    let captureMs = 0;
    let preprocessMs = 0;

    try {
      const captureStart = Date.now();
      const photo = await camera.takePictureAsync({
        quality: 0.5,
        skipProcessing: true,
        base64: false,
        exif: false,
      });
      captureMs = Date.now() - captureStart;

      if (!photo?.uri) {
        throw new Error('No se pudo capturar el frame');
      }

      const preprocessed = await preprocessCapture(photo.uri);
      preprocessMs = preprocessed.preprocessMs;

      const uploadStart = Date.now();
      const response = await predictImage({ uri: preprocessed.uri });
      const uploadNetworkMs = Date.now() - uploadStart - response.inference_ms;
      const cycleMs = Date.now() - cycleStart;

      if (mountedRef.current) {
        setPrediction(response);
        setLastInferenceMs(response.inference_ms);
        setError(null);
        setMetrics({
          captureMs,
          preprocessMs,
          uploadNetworkMs: Math.max(0, uploadNetworkMs),
          serverInferenceMs: response.inference_ms,
          cycleMs,
          resized: preprocessed.resized,
        });
      }

      lastLoggedErrorRef.current = null;

      if (typeof __DEV__ !== 'undefined' && __DEV__) {
        console.log(
          `[EggVision] cycle capture=${captureMs}ms preprocess=${preprocessMs}ms network=${Math.max(0, uploadNetworkMs).toFixed(0)}ms inference=${response.inference_ms}ms total=${cycleMs}ms primary_egg=${response.primary_egg?.confidence?.toFixed(2) ?? 'none'}`,
        );
      }

      return intervalMs;
    } catch (cycleError) {
      const message = getErrorMessage(cycleError);

      if (mountedRef.current) {
        setError(message);
      }

      logCycleWarning(message);

      return isCameraCaptureError(cycleError) ? CAMERA_CAPTURE_BACKOFF_MS : intervalMs;
    } finally {
      inFlightRef.current = false;
      if (mountedRef.current) {
        setIsProcessing(false);
      }
    }
  }, [cameraRef, cameraReady, intervalMs, logCycleWarning]);

  useEffect(() => {
    if (!autoScanEnabled || !cameraReady) {
      return;
    }

    let active = true;

    const loop = async () => {
      await sleep(intervalMs);

      while (active && enabledRef.current) {
        const delayMs = await runCycle();
        if (!active || !enabledRef.current) {
          break;
        }
        await sleep(delayMs);
      }
    };

    void loop();

    return () => {
      active = false;
    };
  }, [autoScanEnabled, cameraReady, intervalMs, runCycle]);

  return {
    autoScanEnabled,
    setAutoScanEnabled,
    isProcessing,
    prediction,
    error,
    lastInferenceMs,
    metrics,
  };
}
