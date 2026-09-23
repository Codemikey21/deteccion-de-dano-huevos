import type { Detection } from '../types/prediction';

export function formatDetectionsSummary(detections: Detection[] | undefined): string {
  if (!detections || detections.length === 0) {
    return 'none';
  }

  return detections
    .map((detection) => `${detection.class_name} ${detection.confidence.toFixed(2)}`)
    .join(', ');
}
