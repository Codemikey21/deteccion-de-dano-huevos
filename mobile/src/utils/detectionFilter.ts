import {
  CRACK_NEAR_EGG_EXPANSION,
  MAX_EGG_AREA_RATIO,
  VISUAL_CRACK_CONFIDENCE,
  VISUAL_EGG_CONFIDENCE,
} from '../constants/detectionVisual';
import type { BBox, Detection } from '../types/prediction';

function bboxArea(bbox: BBox): number {
  return Math.max(0, bbox.x2 - bbox.x1) * Math.max(0, bbox.y2 - bbox.y1);
}

function bboxCenter(bbox: BBox): { x: number; y: number } {
  return {
    x: (bbox.x1 + bbox.x2) / 2,
    y: (bbox.y1 + bbox.y2) / 2,
  };
}

function expandBbox(bbox: BBox, factor: number): BBox {
  const center = bboxCenter(bbox);
  const halfWidth = ((bbox.x2 - bbox.x1) * factor) / 2;
  const halfHeight = ((bbox.y2 - bbox.y1) * factor) / 2;

  return {
    x1: center.x - halfWidth,
    y1: center.y - halfHeight,
    x2: center.x + halfWidth,
    y2: center.y + halfHeight,
  };
}

function isPointInsideBbox(point: { x: number; y: number }, bbox: BBox): boolean {
  return (
    point.x >= bbox.x1 &&
    point.x <= bbox.x2 &&
    point.y >= bbox.y1 &&
    point.y <= bbox.y2
  );
}

export function sanitizeBbox(
  bbox: BBox,
  imageWidth: number,
  imageHeight: number,
): BBox | null {
  const x1 = Math.min(bbox.x1, bbox.x2);
  const x2 = Math.max(bbox.x1, bbox.x2);
  const y1 = Math.min(bbox.y1, bbox.y2);
  const y2 = Math.max(bbox.y1, bbox.y2);

  const clamped = {
    x1: Math.max(0, Math.min(x1, imageWidth)),
    y1: Math.max(0, Math.min(y1, imageHeight)),
    x2: Math.max(0, Math.min(x2, imageWidth)),
    y2: Math.max(0, Math.min(y2, imageHeight)),
  };

  if (clamped.x2 - clamped.x1 < 1 || clamped.y2 - clamped.y1 < 1) {
    return null;
  }

  return clamped;
}

function isReasonableEggSize(
  detection: Detection,
  imageWidth: number,
  imageHeight: number,
): boolean {
  const imageArea = imageWidth * imageHeight;
  if (imageArea <= 0) {
    return false;
  }
  return bboxArea(detection.bbox) / imageArea <= MAX_EGG_AREA_RATIO;
}

function crackNearEgg(crack: Detection, egg: Detection): boolean {
  const crackCenter = bboxCenter(crack.bbox);
  const searchArea = expandBbox(egg.bbox, CRACK_NEAR_EGG_EXPANSION);
  return isPointInsideBbox(crackCenter, searchArea);
}

function pickBestEgg(eggs: Detection[]): Detection | null {
  if (eggs.length === 0) {
    return null;
  }
  return eggs.reduce((best, current) =>
    current.confidence > best.confidence ? current : best,
  );
}

/**
 * Reduce las detecciones crudas del backend a las que deben mostrarse en overlay.
 */
export function filterVisualDetections(
  detections: Detection[],
  imageWidth: number,
  imageHeight: number,
): Detection[] {
  const sanitized = detections
    .map((detection) => {
      const bbox = sanitizeBbox(detection.bbox, imageWidth, imageHeight);
      if (!bbox) {
        return null;
      }
      return { ...detection, bbox };
    })
    .filter((detection): detection is Detection => detection !== null);

  const eggCandidates = sanitized.filter(
    (detection) =>
      detection.class_name === 'egg' &&
      detection.confidence >= VISUAL_EGG_CONFIDENCE &&
      isReasonableEggSize(detection, imageWidth, imageHeight),
  );

  const bestEgg = pickBestEgg(eggCandidates);
  if (!bestEgg) {
    return [];
  }

  const validCracks = sanitized.filter(
    (detection) =>
      detection.class_name === 'crack' &&
      detection.confidence >= VISUAL_CRACK_CONFIDENCE &&
      crackNearEgg(detection, bestEgg),
  );

  return [bestEgg, ...validCracks];
}
