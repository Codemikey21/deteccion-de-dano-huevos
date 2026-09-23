import type { BBox, Detection } from '../types/prediction';

export type PreviewResizeMode = 'cover' | 'contain';

export interface PreviewSize {
  width: number;
  height: number;
}

export interface MappedBBox extends BBox {
  width: number;
  height: number;
}

const MIN_VISIBLE_BOX_PX = 4;
const MIN_VISIBLE_AREA_RATIO = 0.1;

/**
 * Convierte un bbox del espacio de coordenadas de la imagen inferida
 * al espacio visible de la preview de cámara.
 *
 * Modo `cover` (default): escala uniforme max(wRatio, hRatio) y recorta
 * centrado — equivalente a object-fit: cover. Los offsets corrigen el
 * recorte para que las boxes coincidan con lo visible en pantalla.
 *
 * Modo `contain`: letterboxing centrado (object-fit: contain).
 */
export function mapBboxToPreview(
  bbox: BBox,
  imageWidth: number,
  imageHeight: number,
  preview: PreviewSize,
  resizeMode: PreviewResizeMode = 'cover',
): MappedBBox {
  if (imageWidth <= 0 || imageHeight <= 0 || preview.width <= 0 || preview.height <= 0) {
    return { ...bbox, width: 0, height: 0 };
  }

  const scale =
    resizeMode === 'cover'
      ? Math.max(preview.width / imageWidth, preview.height / imageHeight)
      : Math.min(preview.width / imageWidth, preview.height / imageHeight);

  const scaledWidth = imageWidth * scale;
  const scaledHeight = imageHeight * scale;
  const offsetX = (preview.width - scaledWidth) / 2;
  const offsetY = (preview.height - scaledHeight) / 2;

  const x1 = bbox.x1 * scale + offsetX;
  const y1 = bbox.y1 * scale + offsetY;
  const x2 = bbox.x2 * scale + offsetX;
  const y2 = bbox.y2 * scale + offsetY;

  return {
    x1,
    y1,
    x2,
    y2,
    width: x2 - x1,
    height: y2 - y1,
  };
}

/**
 * Recorta un bbox mapeado a los límites del preview.
 * Devuelve null si queda demasiado pequeño o casi fuera de pantalla.
 */
export function clampMappedBBox(
  box: MappedBBox,
  preview: PreviewSize,
): MappedBBox | null {
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

/** Mapea múltiples detecciones a coordenadas de preview. */
export function mapDetectionsToPreview(
  detections: Detection[],
  imageWidth: number,
  imageHeight: number,
  preview: PreviewSize,
  resizeMode: PreviewResizeMode = 'cover',
): Array<Detection & { preview_bbox: MappedBBox }> {
  return detections.map((detection) => ({
    ...detection,
    preview_bbox: mapBboxToPreview(
      detection.bbox,
      imageWidth,
      imageHeight,
      preview,
      resizeMode,
    ),
  }));
}
