/** Umbrales de confianza para cracks. */
export const RAW_CRACK_MIN = 0.25;
export const WEAK_CRACK_MIN = 0.3;
export const STRONG_CRACK_MIN = 0.55;
export const VERY_STRONG_CRACK_MIN = 0.7;

/** Promedio mínimo de confianza en frames con evidencia débil repetida. */
export const TEMPORAL_WEAK_REJECT_AVG = 0.35;

/** Votos temporales en ventana de 5 frames. */
export const TEMPORAL_WINDOW_SIZE = 5;
export const TEMPORAL_STRONG_REJECT_VOTES = 2;
export const TEMPORAL_WEAK_REJECT_VOTES = 3;
export const TEMPORAL_APPROVED_EGG_VOTES = 3;
export const TEMPORAL_APPROVED_MAX_WEAK = 1;

/** Tracker single-egg. */
export const EGG_TRACKER_PERSIST_FRAMES = 2;
export const EGG_TRACKER_LOST_FRAMES = 3;

/** Outlier espacial — rechazar saltos absurdos de bbox en un frame. */
export const OUTLIER_MIN_IOU = 0.1;
export const OUTLIER_MAX_CENTER_SHIFT = 0.35;
export const OUTLIER_MAX_AREA_RATIO = 4.0;
export const MODEL_LOCALIZATION_AREA_RATIO = 0.7;

/** Expansión del bbox del egg para asociar cracks cercanos. */
export const CRACK_NEAR_EGG_EXPANSION = 1.15;

/** Resize antes de upload — lado mayor objetivo. */
export const MAX_UPLOAD_DIMENSION = 1280;
