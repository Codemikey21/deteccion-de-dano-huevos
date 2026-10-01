/** Estados de clasificación devueltos por el backend (raw/debug). */
export type DetectionStatus = 'approved' | 'rejected' | 'unknown';

/** Ruta sugerida por el backend para el flujo operativo. */
export type DetectionRoute = 'accept' | 'reject' | 'review';

export type DetectionReason =
  | 'no_crack_detected'
  | 'crack_detected'
  | 'egg_not_detected'
  | 'crack_without_confirmed_egg';

/** Estado único para UX. */
export type DisplayStatus = 'detecting' | 'approved' | 'rejected' | 'review';

export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface NormalizedBBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: BBox;
  bbox_normalized?: NormalizedBBox;
}

export interface PrimaryEgg {
  confidence: number;
  bbox: BBox;
  bbox_normalized: NormalizedBBox;
}

export interface ImageInfo {
  width: number;
  height: number;
}

export interface ModelInfo {
  name: string;
  imgsz: number;
}

export interface EggResult extends PrimaryEgg {
  /** Number within the current frame, not a persistent tracking ID. */
  id: number;
  status: 'healthy' | 'damaged';
  damage_source: 'none' | 'dark_line' | 'yolo_crack' | 'both';
  dark_line_area_ratio: number;
  cracks: Detection[];
}

export interface EggSummary {
  total: number;
  healthy: number;
  damaged: number;
}

export interface PredictionResponse {
  eggs?: EggResult[] | null;
  summary?: EggSummary | null;
  timing?: { full_frame_ms: number; roi_analysis_ms: number; total_ms: number } | null;
  status: DetectionStatus;
  route: DetectionRoute;
  reason: DetectionReason;
  egg_detected: boolean;
  crack_detected: boolean;
  image: ImageInfo;
  /** Fuente única de verdad para el huevo visible. */
  primary_egg?: PrimaryEgg | null;
  /** Cracks espacialmente asociados al primary_egg. */
  cracks?: Detection[];
  raw_detections?: Detection[];
  detections: Detection[];
  inference_ms: number;
  model: ModelInfo;
}

export interface HealthResponse {
  status: string;
  service: string;
  model_loaded: boolean;
  model: string;
  input_size: number;
  model_path?: string | null;
  model_error?: string | null;
}
