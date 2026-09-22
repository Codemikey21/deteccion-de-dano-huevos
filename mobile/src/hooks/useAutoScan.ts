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

export interface UseAutoScanOptions {
  cameraRef: RefObject<CameraView | null>;
  /** Desactivado por defecto hasta validar el flujo end-to-end. */
  enabled?: boolean;
  intervalMs?: number;
}

export interface UseAutoScanResult {
  enabled: boolean;
  setEnabled: Dispatch<SetStateAction<boolean>>;
  isProcessing: boolean;
  lastResult: PredictionResponse | null;
  lastError: string | null;
  /** Disparo manual de un ciclo (útil para pruebas). */
  captureOnce: () => Promise<void>;
}

/**
 * Hook preparado para auto-detección periódica.
 * Evita requests simultáneos y deja listo el envío a POST /predict.
 */
export function useAutoScan({
  cameraRef,
  enabled: enabledProp = false,
  intervalMs = SCAN_INTERVAL_MS,
}: UseAutoScanOptions): UseAutoScanResult {
  const [enabled, setEnabled] = useState(enabledProp);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResult, setLastResult] = useState<PredictionResponse | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);
  const inFlightRef = useRef(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const captureOnce = useCallback(async () => {
    if (inFlightRef.current) {
      return;
    }

    const camera = cameraRef.current;
    if (!camera) {
      if (mountedRef.current) {
        setLastError('Cámara no disponible');
      }
      return;
    }

    inFlightRef.current = true;
    if (mountedRef.current) {
      setIsProcessing(true);
      setLastError(null);
    }

    try {
      const photo = await camera.takePictureAsync({
        quality: 0.6,
        skipProcessing: true,
      });

      if (!photo?.uri) {
        throw new Error('No se pudo capturar el frame');
      }

      const response = await predictImage({ uri: photo.uri });
      if (mountedRef.current) {
        setLastResult(response);
      }
    } catch (error) {
      if (mountedRef.current) {
        const message = error instanceof Error ? error.message : 'Error de inferencia';
        setLastError(message);
      }
    } finally {
      inFlightRef.current = false;
      if (mountedRef.current) {
        setIsProcessing(false);
      }
    }
  }, [cameraRef]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const timer = setInterval(() => {
      if (!inFlightRef.current) {
        void captureOnce();
      }
    }, intervalMs);

    return () => clearInterval(timer);
  }, [enabled, intervalMs, captureOnce]);

  return {
    enabled,
    setEnabled,
    isProcessing,
    lastResult,
    lastError,
    captureOnce,
  };
}
