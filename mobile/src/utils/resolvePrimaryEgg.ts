import type { Detection, ImageInfo, PredictionResponse, PrimaryEgg } from '../types/prediction';

const LEGACY_EGG_MIN = 0.3;
const IMPOSSIBLE_AREA_RATIO = 0.98;

function normalizeBbox(
  bbox: Detection['bbox'],
  image: ImageInfo,
): PrimaryEgg['bbox_normalized'] {
  return {
    x1: bbox.x1 / image.width,
    y1: bbox.y1 / image.height,
    x2: bbox.x2 / image.width,
    y2: bbox.y2 / image.height,
  };
}

function isImpossibleEgg(detection: Detection, image: ImageInfo): boolean {
  const width = Math.max(0, detection.bbox.x2 - detection.bbox.x1);
  const height = Math.max(0, detection.bbox.y2 - detection.bbox.y1);
  if (width <= 0 || height <= 0) {
    return true;
  }
  const areaRatio = (width * height) / (image.width * image.height);
  return areaRatio >= IMPOSSIBLE_AREA_RATIO;
}

/**
 * Fallback solo para backends legacy sin `primary_egg` (p.ej. AWS pendiente redeploy).
 * Replica la selección mínima del backend: egg >= 0.30, mayor confidence, sin filtros agresivos.
 */
export function deriveLegacyPrimaryEgg(
  detections: Detection[],
  image: ImageInfo,
): PrimaryEgg | null {
  const candidates = detections.filter(
    (detection) =>
      detection.class_name === 'egg' &&
      detection.confidence >= LEGACY_EGG_MIN &&
      !isImpossibleEgg(detection, image),
  );

  if (candidates.length === 0) {
    return null;
  }

  const best = candidates.reduce((current, next) =>
    next.confidence > current.confidence ? next : current,
  );

  return {
    confidence: best.confidence,
    bbox: best.bbox,
    bbox_normalized: best.bbox_normalized ?? normalizeBbox(best.bbox, image),
  };
}

export function resolvePrimaryEgg(prediction: PredictionResponse): PrimaryEgg | null {
  if (prediction.primary_egg) {
    return prediction.primary_egg;
  }

  const raw = prediction.raw_detections ?? prediction.detections;
  return deriveLegacyPrimaryEgg(raw, prediction.image);
}
