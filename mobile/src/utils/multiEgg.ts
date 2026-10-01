import type { EggResult, EggSummary, PredictionResponse } from '../types/prediction';

/** Null means old backend: preserve the existing single-egg presentation. */
export function getMultiEggResult(prediction: PredictionResponse | null): {
  eggs: EggResult[]; summary: EggSummary;
} | null {
  if (!Array.isArray(prediction?.eggs)) return null;
  const eggs = prediction.eggs;
  const damaged = eggs.filter((egg) => egg.status === 'damaged').length;
  return { eggs, summary: { total: eggs.length, healthy: eggs.length - damaged, damaged } };
}

export function damageLabel(source: EggResult['damage_source']): string {
  switch (source) {
    case 'dark_line': return 'marca oscura visible';
    case 'yolo_crack': return 'grieta detectada por modelo';
    case 'both': return 'raya oscura y grieta del modelo';
    default: return 'sin daño visible detectado';
  }
}
