import type { NormalizedBBox } from '../types/prediction';

export interface PreviewSize {
  width: number;
  height: number;
}

export interface MappedBBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
}

export type OrientationFix = 'none' | 'rotate90cw' | 'rotate90ccw';

export interface BboxTransformDebug {
  sourceWidth: number;
  sourceHeight: number;
  previewWidth: number;
  previewHeight: number;
  orientationFix: OrientationFix;
  effectiveSourceWidth: number;
  effectiveSourceHeight: number;
  scale: number;
  cropX: number;
  cropY: number;
  normalizedInput: NormalizedBBox;
  normalizedAfterOrientation: NormalizedBBox;
  sourcePixels: BBox;
  mappedPixels: MappedBBox;
  areaRatio: number;
}

interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

const MIN_VISIBLE_BOX_PX = 4;
const MIN_VISIBLE_AREA_RATIO = 0.1;

export function detectOrientationFix(
  sourceWidth: number,
  sourceHeight: number,
  previewWidth: number,
  previewHeight: number,
): OrientationFix {
  if (sourceWidth <= 0 || sourceHeight <= 0 || previewWidth <= 0 || previewHeight <= 0) {
    return 'none';
  }

  const sourceLandscape = sourceWidth > sourceHeight;
  const previewPortrait = previewHeight > previewWidth;
  const sourcePortrait = sourceHeight > sourceWidth;
  const previewLandscape = previewWidth > previewHeight;

  if (sourceLandscape && previewPortrait) {
    return 'rotate90cw';
  }
  if (sourcePortrait && previewLandscape) {
    return 'rotate90ccw';
  }

  return 'none';
}

export function getEffectiveSourceDimensions(
  sourceWidth: number,
  sourceHeight: number,
  orientationFix: OrientationFix,
): { width: number; height: number } {
  if (orientationFix === 'none') {
    return { width: sourceWidth, height: sourceHeight };
  }
  return { width: sourceHeight, height: sourceWidth };
}

export function rotateNormalizedBBox90CW(bbox: NormalizedBBox): NormalizedBBox {
  const corners = [
    { x: bbox.x1, y: bbox.y1 },
    { x: bbox.x2, y: bbox.y1 },
    { x: bbox.x1, y: bbox.y2 },
    { x: bbox.x2, y: bbox.y2 },
  ].map(({ x, y }) => ({ x: y, y: 1 - x }));

  const xs = corners.map((corner) => corner.x);
  const ys = corners.map((corner) => corner.y);
  return {
    x1: Math.min(...xs),
    y1: Math.min(...ys),
    x2: Math.max(...xs),
    y2: Math.max(...ys),
  };
}

export function rotateNormalizedBBox90CCW(bbox: NormalizedBBox): NormalizedBBox {
  const corners = [
    { x: bbox.x1, y: bbox.y1 },
    { x: bbox.x2, y: bbox.y1 },
    { x: bbox.x1, y: bbox.y2 },
    { x: bbox.x2, y: bbox.y2 },
  ].map(({ x, y }) => ({ x: 1 - y, y: x }));

  const xs = corners.map((corner) => corner.x);
  const ys = corners.map((corner) => corner.y);
  return {
    x1: Math.min(...xs),
    y1: Math.min(...ys),
    x2: Math.max(...xs),
    y2: Math.max(...ys),
  };
}

export function applyOrientationFix(
  bbox: NormalizedBBox,
  orientationFix: OrientationFix,
): NormalizedBBox {
  if (orientationFix === 'rotate90cw') {
    return rotateNormalizedBBox90CW(bbox);
  }
  if (orientationFix === 'rotate90ccw') {
    return rotateNormalizedBBox90CCW(bbox);
  }
  return bbox;
}

export function normalizedToSourcePixels(
  bbox: NormalizedBBox,
  sourceWidth: number,
  sourceHeight: number,
): BBox {
  return {
    x1: bbox.x1 * sourceWidth,
    y1: bbox.y1 * sourceHeight,
    x2: bbox.x2 * sourceWidth,
    y2: bbox.y2 * sourceHeight,
  };
}

export function normalizedAreaRatio(bbox: NormalizedBBox): number {
  const width = Math.max(0, bbox.x2 - bbox.x1);
  const height = Math.max(0, bbox.y2 - bbox.y1);
  return width * height;
}

/**
 * Transforma bbox normalizado al espacio visible del preview (object-fit: cover).
 */
export function mapNormalizedBboxToPreview(
  normalized: NormalizedBBox,
  sourceWidth: number,
  sourceHeight: number,
  preview: PreviewSize,
  orientationFix: OrientationFix = 'none',
): MappedBBox {
  if (sourceWidth <= 0 || sourceHeight <= 0 || preview.width <= 0 || preview.height <= 0) {
    return { x1: 0, y1: 0, x2: 0, y2: 0, width: 0, height: 0 };
  }

  const oriented = applyOrientationFix(normalized, orientationFix);
  const effective = getEffectiveSourceDimensions(sourceWidth, sourceHeight, orientationFix);
  const sourcePixels = normalizedToSourcePixels(
    oriented,
    effective.width,
    effective.height,
  );

  const scale = Math.max(
    preview.width / effective.width,
    preview.height / effective.height,
  );
  const scaledWidth = effective.width * scale;
  const scaledHeight = effective.height * scale;
  const cropX = (scaledWidth - preview.width) / 2;
  const cropY = (scaledHeight - preview.height) / 2;

  const x1 = sourcePixels.x1 * scale - cropX;
  const y1 = sourcePixels.y1 * scale - cropY;
  const x2 = sourcePixels.x2 * scale - cropX;
  const y2 = sourcePixels.y2 * scale - cropY;

  return {
    x1,
    y1,
    x2,
    y2,
    width: x2 - x1,
    height: y2 - y1,
  };
}

export function buildBboxTransformDebug(
  normalized: NormalizedBBox,
  sourceWidth: number,
  sourceHeight: number,
  preview: PreviewSize,
  orientationFix: OrientationFix = detectOrientationFix(
    sourceWidth,
    sourceHeight,
    preview.width,
    preview.height,
  ),
): BboxTransformDebug {
  const oriented = applyOrientationFix(normalized, orientationFix);
  const effective = getEffectiveSourceDimensions(sourceWidth, sourceHeight, orientationFix);
  const sourcePixels = normalizedToSourcePixels(oriented, effective.width, effective.height);
  const mappedPixels = mapNormalizedBboxToPreview(
    normalized,
    sourceWidth,
    sourceHeight,
    preview,
    orientationFix,
  );
  const scale = Math.max(
    preview.width / effective.width,
    preview.height / effective.height,
  );
  const scaledWidth = effective.width * scale;
  const scaledHeight = effective.height * scale;

  return {
    sourceWidth,
    sourceHeight,
    previewWidth: preview.width,
    previewHeight: preview.height,
    orientationFix,
    effectiveSourceWidth: effective.width,
    effectiveSourceHeight: effective.height,
    scale,
    cropX: (scaledWidth - preview.width) / 2,
    cropY: (scaledHeight - preview.height) / 2,
    normalizedInput: normalized,
    normalizedAfterOrientation: oriented,
    sourcePixels,
    mappedPixels,
    areaRatio: normalizedAreaRatio(normalized),
  };
}

export function clampMappedBBox(box: MappedBBox, preview: PreviewSize): MappedBBox | null {
  const originalArea = Math.max(box.width * box.height, 1);

  const x1 = Math.max(0, Math.min(box.x1, preview.width));
  const y1 = Math.max(0, Math.min(box.y1, preview.height));
  const x2 = Math.max(0, Math.min(box.x2, preview.width));
  const y2 = Math.max(0, Math.min(box.y2, preview.height));

  const width = x2 - x1;
  const height = y2 - y1;

  if (width < MIN_VISIBLE_BOX_PX || height < MIN_VISIBLE_BOX_PX) {
    return null;
  }

  const visibleArea = width * height;
  if (visibleArea / originalArea < MIN_VISIBLE_AREA_RATIO) {
    return null;
  }

  return { x1, y1, x2, y2, width, height };
}
