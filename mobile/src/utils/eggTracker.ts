import {
  EGG_TRACKER_LOST_FRAMES,
  EGG_TRACKER_PERSIST_FRAMES,
  MODEL_LOCALIZATION_AREA_RATIO,
  OUTLIER_MAX_AREA_RATIO,
  OUTLIER_MAX_CENTER_SHIFT,
  OUTLIER_MIN_IOU,
} from '../constants/detectionVisual';
import type { NormalizedBBox, PrimaryEgg } from '../types/prediction';
import { normalizedAreaRatio } from './bboxTransform';

export type EggTrackerPhase = 'seen' | 'persisted' | 'lost';

export interface TrackedEgg {
  egg: PrimaryEgg;
  phase: EggTrackerPhase;
  missedFrames: number;
  outlierRejected: boolean;
  modelLocalizationError: boolean;
}

export interface EggTrackerState {
  tracked: TrackedEgg | null;
}

function bboxCenter(bbox: NormalizedBBox): { x: number; y: number } {
  return {
    x: (bbox.x1 + bbox.x2) / 2,
    y: (bbox.y1 + bbox.y2) / 2,
  };
}

function bboxIoU(a: NormalizedBBox, b: NormalizedBBox): number {
  const x1 = Math.max(a.x1, b.x1);
  const y1 = Math.max(a.y1, b.y1);
  const x2 = Math.min(a.x2, b.x2);
  const y2 = Math.min(a.y2, b.y2);
  if (x2 <= x1 || y2 <= y1) {
    return 0;
  }
  const intersection = (x2 - x1) * (y2 - y1);
  const areaA = normalizedAreaRatio(a);
  const areaB = normalizedAreaRatio(b);
  const union = areaA + areaB - intersection;
  return union > 0 ? intersection / union : 0;
}

export function isSpatialOutlier(
  next: NormalizedBBox,
  previous: NormalizedBBox,
): boolean {
  const iou = bboxIoU(next, previous);
  const nextCenter = bboxCenter(next);
  const prevCenter = bboxCenter(previous);
  const centerShift = Math.hypot(
    nextCenter.x - prevCenter.x,
    nextCenter.y - prevCenter.y,
  );

  const nextArea = Math.max(normalizedAreaRatio(next), 0.0001);
  const prevArea = Math.max(normalizedAreaRatio(previous), 0.0001);
  const areaRatio = nextArea / prevArea;

  if (iou < OUTLIER_MIN_IOU && centerShift > OUTLIER_MAX_CENTER_SHIFT) {
    return true;
  }

  if (areaRatio > OUTLIER_MAX_AREA_RATIO || areaRatio < 1 / OUTLIER_MAX_AREA_RATIO) {
    return true;
  }

  return false;
}

export function detectModelLocalizationError(
  next: NormalizedBBox,
  previous: NormalizedBBox | null,
): boolean {
  const nextArea = normalizedAreaRatio(next);
  if (nextArea < MODEL_LOCALIZATION_AREA_RATIO) {
    return false;
  }
  if (!previous) {
    return nextArea >= MODEL_LOCALIZATION_AREA_RATIO;
  }
  const prevArea = normalizedAreaRatio(previous);
  return nextArea >= MODEL_LOCALIZATION_AREA_RATIO && nextArea > prevArea * 2.5;
}

export function updateEggTracker(
  state: EggTrackerState,
  primaryEgg: PrimaryEgg | null | undefined,
): EggTrackerState {
  if (primaryEgg) {
    const previous = state.tracked?.egg.bbox_normalized ?? null;
    const outlier = previous ? isSpatialOutlier(primaryEgg.bbox_normalized, previous) : false;
    const modelLocalizationError = detectModelLocalizationError(
      primaryEgg.bbox_normalized,
      previous,
    );

    if (outlier && state.tracked) {
      const missedFrames = state.tracked.missedFrames + 1;
      if (missedFrames >= EGG_TRACKER_LOST_FRAMES) {
        return { tracked: null };
      }

      return {
        tracked: {
          ...state.tracked,
          phase: 'persisted',
          missedFrames,
          outlierRejected: true,
          modelLocalizationError,
        },
      };
    }

    return {
      tracked: {
        egg: primaryEgg,
        phase: 'seen',
        missedFrames: 0,
        outlierRejected: false,
        modelLocalizationError,
      },
    };
  }

  if (!state.tracked) {
    return { tracked: null };
  }

  const missedFrames = state.tracked.missedFrames + 1;
  if (missedFrames > EGG_TRACKER_PERSIST_FRAMES) {
    if (missedFrames >= EGG_TRACKER_LOST_FRAMES) {
      return { tracked: null };
    }
    return {
      tracked: {
        ...state.tracked,
        phase: 'lost',
        missedFrames,
      },
    };
  }

  return {
    tracked: {
      ...state.tracked,
      phase: 'persisted',
      missedFrames,
    },
  };
}

export function resetEggTracker(): EggTrackerState {
  return { tracked: null };
}
