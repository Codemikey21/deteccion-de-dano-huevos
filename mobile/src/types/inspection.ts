export type InspectionStatus = 'approved' | 'rejected';

export interface Inspection {
  id: string;
  timestamp: string;
  status: InspectionStatus;
  crackDetected: boolean;
  eggConfidence?: number;
  crackConfidence?: number;
  inferenceMs?: number;
}

export interface InspectionStats {
  total: number;
  approved: number;
  rejected: number;
  approvedPct: number;
  rejectedPct: number;
  lastInspection: Inspection | null;
  avgInferenceMs: number | null;
}
