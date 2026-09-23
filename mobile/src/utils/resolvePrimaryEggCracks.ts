import { CRACK_NEAR_EGG_EXPANSION, WEAK_CRACK_MIN } from '../constants/detectionVisual';
import type { Detection, PredictionResponse, PrimaryEgg } from '../types/prediction';

function expandBbox(bbox: Detection['bbox'], factor: number): Detection['bbox'] {
  const cx = (bbox.x1 + bbox.x2) / 2;
  const cy = (bbox.y1 + bbox.y2) / 2;
  const halfW = ((bbox.x2 - bbox.x1) * factor) / 2;
  const halfH = ((bbox.y2 - bbox.y1) * factor) / 2;
  return {
    x1: cx - halfW,
    y1: cy - halfH,
    x2: cx + halfW,
    y2: cy + halfH,
  };
}

function isCrackNearEgg(crack: Detection, egg: PrimaryEgg): boolean {
  const center = {
    x: (crack.bbox.x1 + crack.bbox.x2) / 2,
    y: (crack.bbox.y1 + crack.bbox.y2) / 2,
  };
  const expanded = expandBbox(egg.bbox, CRACK_NEAR_EGG_EXPANSION);
  return (
    center.x >= expanded.x1 &&
    center.x <= expanded.x2 &&
    center.y >= expanded.y1 &&
    center.y <= expanded.y2
  );
}

/** Fallback de cracks asociados cuando backend legacy no envía `cracks`. */
export function getCracksForPrimaryEggFromRaw(
  prediction: PredictionResponse,
  primaryEgg: PrimaryEgg,
): Detection[] {
  const raw = prediction.raw_detections ?? prediction.detections;
  return raw
    .filter(
      (detection) =>
        detection.class_name === 'crack' &&
        detection.confidence >= WEAK_CRACK_MIN &&
        isCrackNearEgg(detection, primaryEgg),
    )
    .sort((a, b) => b.confidence - a.confidence);
}
