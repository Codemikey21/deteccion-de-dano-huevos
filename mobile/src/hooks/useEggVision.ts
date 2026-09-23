import { useEffect, useMemo, useRef, useState } from 'react';

import type { DisplayStatus, PredictionResponse } from '../types/prediction';
import {
  buildBboxTransformDebug,
  clampMappedBBox,
  detectOrientationFix,
  mapNormalizedBboxToPreview,
  type BboxTransformDebug,
  type PreviewSize,
} from '../utils/bboxTransform';
import {
  appendFrameCrackEvidence,
  buildFrameFromPrediction,
  computeTemporalCrackDecision,
  formatTemporalCrackLabel,
  getCrackEvidenceForPrimaryEgg,
  getCracksForPrimaryEgg,
  type CrackEvidenceResult,
  type FrameCrackEvidence,
  type TemporalCrackDecision,
} from '../utils/crackEvidence';
import { resolvePrimaryEgg } from '../utils/resolvePrimaryEgg';
import { computeDisplayStatus } from '../utils/displayStatus';
import {
  resetEggTracker,
  updateEggTracker,
  type EggTrackerState,
  type TrackedEgg,
} from '../utils/eggTracker';

export interface VisualBox {
  className: 'egg' | 'crack';
  confidence: number;
  color: string;
  previewBbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  };
}

export interface UseEggVisionResult {
  trackedEgg: TrackedEgg | null;
  tracker: EggTrackerState;
  currentFrame: FrameCrackEvidence | null;
  temporal: TemporalCrackDecision | null;
  temporalCracksLabel: string;
  displayStatus: DisplayStatus;
  crackEvidence: CrackEvidenceResult | null;
  visualBoxes: VisualBox[];
  bboxDebug: BboxTransformDebug | null;
  associatedCracks: ReturnType<typeof getCracksForPrimaryEgg>;
}

function crackColor(
  level: 'weak' | 'strong' | 'very_strong',
  displayStatus: DisplayStatus,
  temporalReason: string | null,
): string {
  if (displayStatus === 'rejected') {
    return '#ef4444';
  }
  if (level === 'very_strong' || level === 'strong') {
    return '#ef4444';
  }
  if (level === 'weak' && temporalReason === 'temporal_repeated_weak_crack') {
    return '#ef4444';
  }
  return '#f59e0b';
}

export function useEggVision(
  prediction: PredictionResponse | null,
  preview: PreviewSize,
  autoScanEnabled: boolean,
): UseEggVisionResult {
  const [tracker, setTracker] = useState<EggTrackerState>(resetEggTracker());
  const [window, setWindow] = useState<FrameCrackEvidence[]>([]);
  const [currentFrame, setCurrentFrame] = useState<FrameCrackEvidence | null>(null);
  const lastPredictionRef = useRef<PredictionResponse | null>(null);

  useEffect(() => {
    if (!autoScanEnabled) {
      setTracker(resetEggTracker());
      setWindow([]);
      setCurrentFrame(null);
      lastPredictionRef.current = null;
    }
  }, [autoScanEnabled]);

  useEffect(() => {
    if (!autoScanEnabled || !prediction) {
      return;
    }

    if (lastPredictionRef.current === prediction) {
      return;
    }
    lastPredictionRef.current = prediction;

    const frame = buildFrameFromPrediction(prediction);
    setCurrentFrame(frame);
    setWindow((current) => appendFrameCrackEvidence(current, frame));
    setTracker((current) => updateEggTracker(current, resolvePrimaryEgg(prediction)));
  }, [autoScanEnabled, prediction]);

  const temporal = useMemo(() => {
    if (window.length === 0) {
      return null;
    }
    return computeTemporalCrackDecision(window);
  }, [window]);

  const displayStatus = computeDisplayStatus(tracker, temporal, autoScanEnabled);
  const associatedCracks = prediction ? getCracksForPrimaryEgg(prediction) : [];
  const crackEvidence = prediction
    ? getCrackEvidenceForPrimaryEgg(associatedCracks)
    : null;

  const bboxDebug = useMemo(() => {
    const egg = tracker.tracked?.egg;
    if (!egg || preview.width <= 0 || preview.height <= 0 || !prediction) {
      return null;
    }

    return buildBboxTransformDebug(
      egg.bbox_normalized,
      prediction.image.width,
      prediction.image.height,
      preview,
      detectOrientationFix(
        prediction.image.width,
        prediction.image.height,
        preview.width,
        preview.height,
      ),
    );
  }, [tracker.tracked?.egg, prediction, preview]);

  const visualBoxes = useMemo((): VisualBox[] => {
    const egg = tracker.tracked?.egg;
    if (!egg || preview.width <= 0 || preview.height <= 0 || !prediction) {
      return [];
    }

    const orientationFix = detectOrientationFix(
      prediction.image.width,
      prediction.image.height,
      preview.width,
      preview.height,
    );

    const eggMapped = clampMappedBBox(
      mapNormalizedBboxToPreview(
        egg.bbox_normalized,
        prediction.image.width,
        prediction.image.height,
        preview,
        orientationFix,
      ),
      preview,
    );

    if (!eggMapped) {
      return [];
    }

    const boxes: VisualBox[] = [
      {
        className: 'egg',
        confidence: egg.confidence,
        color: '#22c55e',
        previewBbox: eggMapped,
      },
    ];

    const cracksToShow = crackEvidence?.relatedCracks ?? [];
    const showWeak = displayStatus === 'rejected' && temporal?.reason === 'temporal_repeated_weak_crack';

    for (const crack of cracksToShow) {
      const normalized = crack.bbox_normalized;
      if (!normalized) {
        continue;
      }

      const level = crack.confidence >= 0.7 ? 'very_strong' : crack.confidence >= 0.55 ? 'strong' : 'weak';
      if (level === 'weak' && !showWeak && displayStatus !== 'review') {
        continue;
      }

      const mapped = clampMappedBBox(
        mapNormalizedBboxToPreview(
          normalized,
          prediction.image.width,
          prediction.image.height,
          preview,
          orientationFix,
        ),
        preview,
      );

      if (!mapped) {
        continue;
      }

      boxes.push({
        className: 'crack',
        confidence: crack.confidence,
        color: crackColor(level, displayStatus, temporal?.reason ?? null),
        previewBbox: mapped,
      });
    }

    if (
      displayStatus === 'rejected' &&
      temporal?.reason === 'temporal_repeated_weak_crack' &&
      crackEvidence?.representativeCrack?.bbox_normalized
    ) {
      const rep = crackEvidence.representativeCrack;
      const alreadyShown = boxes.some((box) => box.className === 'crack');
      if (!alreadyShown && rep.bbox_normalized) {
        const mapped = clampMappedBBox(
          mapNormalizedBboxToPreview(
            rep.bbox_normalized,
            prediction.image.width,
            prediction.image.height,
            preview,
            orientationFix,
          ),
          preview,
        );
        if (mapped) {
          boxes.push({
            className: 'crack',
            confidence: rep.confidence,
            color: '#ef4444',
            previewBbox: mapped,
          });
        }
      }
    }

    return boxes;
  }, [tracker.tracked?.egg, prediction, preview, crackEvidence, displayStatus, temporal?.reason]);

  const temporalCracksLabel = window.map(formatTemporalCrackLabel).join(' | ');

  return {
    trackedEgg: tracker.tracked,
    tracker,
    currentFrame,
    temporal,
    temporalCracksLabel,
    displayStatus,
    crackEvidence,
    visualBoxes,
    bboxDebug,
    associatedCracks,
  };
}
