import { useEffect, useMemo, useState } from 'react';

import type { PredictionResponse } from '../types/prediction';
import {
  appendFrameToWindow,
  computeStabilizedClassification,
  formatWindowSnapshot,
  STABILIZATION_WINDOW_SIZE,
  type FrameSnapshot,
  type StabilizedClassification,
} from '../utils/statusStabilization';

export interface UseStabilizedClassificationResult {
  stabilized: StabilizedClassification | null;
  window: FrameSnapshot[];
  windowLabel: string;
}

export function useStabilizedClassification(
  rawPrediction: PredictionResponse | null,
  enabled: boolean,
): UseStabilizedClassificationResult {
  const [window, setWindow] = useState<FrameSnapshot[]>([]);

  useEffect(() => {
    if (!enabled) {
      setWindow([]);
    }
  }, [enabled]);

  useEffect(() => {
    if (!enabled || !rawPrediction) {
      return;
    }
    setWindow((current) => appendFrameToWindow(current, rawPrediction, STABILIZATION_WINDOW_SIZE));
  }, [enabled, rawPrediction]);

  const stabilized = useMemo(() => {
    if (window.length === 0) {
      return null;
    }
    return computeStabilizedClassification(window);
  }, [window]);

  const windowLabel = window.map(formatWindowSnapshot).join(' | ');

  return {
    stabilized,
    window,
    windowLabel,
  };
}
