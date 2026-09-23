/** Umbrales mínimos de confidence para dibujar detecciones en el overlay. */
export const VISUAL_EGG_CONFIDENCE = 0.4;
export const VISUAL_CRACK_CONFIDENCE = 0.55;

/** Máxima fracción del área de imagen que puede ocupar un egg visible. */
export const MAX_EGG_AREA_RATIO = 0.85;

/** Expansión del bbox del egg para considerar cracks cercanos (factor uniforme). */
export const CRACK_NEAR_EGG_EXPANSION = 1.15;
