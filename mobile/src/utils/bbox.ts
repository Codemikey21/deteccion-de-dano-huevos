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
