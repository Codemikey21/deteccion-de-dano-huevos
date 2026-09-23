import {
  STRONG_CRACK_MIN,
  TEMPORAL_APPROVED_EGG_VOTES,
  TEMPORAL_APPROVED_MAX_WEAK,
  TEMPORAL_STRONG_REJECT_VOTES,
  TEMPORAL_WEAK_REJECT_AVG,
  TEMPORAL_WEAK_REJECT_VOTES,
  TEMPORAL_WINDOW_SIZE,
  VERY_STRONG_CRACK_MIN,
  WEAK_CRACK_MIN,
} from '../constants/detectionVisual';
import type {
  Detection,
  DetectionRoute,
  DetectionStatus,
  PredictionResponse,
  PrimaryEgg,
} from '../types/prediction';
import { resolvePrimaryEgg } from './resolvePrimaryEgg';
import { getCracksForPrimaryEggFromRaw } from './resolvePrimaryEggCracks';

export type CrackLevel = 'none' | 'weak' | 'strong' | 'very_strong';

export interface CrackEvidenceResult {
  strongestConfidence: number | null;
  level: CrackLevel;
  relatedCracks: Detection[];
  representativeCrack: Detection | null;
}

export interface FrameCrackEvidence {
  eggDetected: boolean;
  strongestCrackConfidence: number | null;
  crackLevel: CrackLevel;
  primaryEgg: PrimaryEgg | null;
  currentEvidence: CrackEvidenceResult | null;
}

export interface TemporalCrackDecision {
  status: DetectionStatus;
  route: DetectionRoute;
  reason: string;
  window: FrameCrackEvidence[];
  strongVotes: number;
  veryStrongVotes: number;
  weakVotes: number;
  eggVotes: number;
  avgCrackConfidence: number | null;
}

export function classifyCrackLevel(confidence: number | null): CrackLevel {
  if (confidence === null || confidence < WEAK_CRACK_MIN) {
    return 'none';
  }
  if (confidence >= VERY_STRONG_CRACK_MIN) {
    return 'very_strong';
  }
  if (confidence >= STRONG_CRACK_MIN) {
    return 'strong';
  }
  return 'weak';
}

/** Cracks asociados al primary_egg — backend primero, fallback legacy. */
export function getCracksForPrimaryEgg(
  prediction: PredictionResponse,
  primaryEgg?: PrimaryEgg | null,
): Detection[] {
  if (prediction.primary_egg && prediction.cracks) {
    return prediction.cracks;
  }

  const egg = primaryEgg ?? resolvePrimaryEgg(prediction);
  if (!egg) {
    return [];
  }

  return getCracksForPrimaryEggFromRaw(prediction, egg);
}

export function getCrackEvidenceForPrimaryEgg(
  cracks: Detection[],
): CrackEvidenceResult {
  const relatedCracks = cracks.filter((crack) => crack.confidence >= WEAK_CRACK_MIN);

  if (relatedCracks.length === 0) {
    return {
      strongestConfidence: null,
      level: 'none',
      relatedCracks: [],
      representativeCrack: null,
    };
  }

  const strongest = relatedCracks.reduce((best, current) =>
    current.confidence > best.confidence ? current : best,
  );

  return {
    strongestConfidence: strongest.confidence,
    level: classifyCrackLevel(strongest.confidence),
    relatedCracks,
    representativeCrack: strongest,
  };
}

export function buildFrameFromPrediction(
  prediction: PredictionResponse,
): FrameCrackEvidence {
  const primaryEgg = resolvePrimaryEgg(prediction);
  if (!primaryEgg) {
    return {
      eggDetected: false,
      strongestCrackConfidence: null,
      crackLevel: 'none',
      primaryEgg: null,
      currentEvidence: null,
    };
  }

  const currentEvidence = getCrackEvidenceForPrimaryEgg(
    getCracksForPrimaryEgg(prediction, primaryEgg),
  );
  return {
    eggDetected: true,
    strongestCrackConfidence: currentEvidence.strongestConfidence,
    crackLevel: currentEvidence.level,
    primaryEgg,
    currentEvidence,
  };
}

export function appendFrameCrackEvidence(
  window: FrameCrackEvidence[],
  frame: FrameCrackEvidence,
  windowSize: number = TEMPORAL_WINDOW_SIZE,
): FrameCrackEvidence[] {
  const next = [...window, frame];
  if (next.length <= windowSize) {
    return next;
  }
  return next.slice(next.length - windowSize);
}

export function formatTemporalCrackLabel(frame: FrameCrackEvidence): string {
  if (frame.crackLevel === 'none') {
    return 'none';
  }
  return `${frame.crackLevel} ${frame.strongestCrackConfidence?.toFixed(2) ?? '?'}`;
}

export function computeTemporalCrackDecision(
  window: FrameCrackEvidence[],
): TemporalCrackDecision {
  const veryStrongVotes = window.filter((frame) => frame.crackLevel === 'very_strong').length;
  const strongVotes = window.filter((frame) => frame.crackLevel === 'strong').length;
  const weakVotes = window.filter((frame) => frame.crackLevel === 'weak').length;
  const eggVotes = window.filter((frame) => frame.eggDetected).length;
  const evidenceFrames = window.filter((frame) => frame.crackLevel !== 'none');
  const avgCrackConfidence =
    evidenceFrames.length > 0
      ? evidenceFrames.reduce(
          (sum, frame) => sum + (frame.strongestCrackConfidence ?? 0),
          0,
        ) / evidenceFrames.length
      : null;

  const base = {
    window,
    strongVotes,
    veryStrongVotes,
    weakVotes,
    eggVotes,
    avgCrackConfidence,
  };

  const hasVeryStrongWithEgg = window.some(
    (frame) => frame.eggDetected && frame.crackLevel === 'very_strong',
  );
  if (hasVeryStrongWithEgg) {
    return {
      ...base,
      status: 'rejected',
      route: 'reject',
      reason: 'very_strong_crack',
    };
  }

  if (eggVotes === 0) {
    return {
      ...base,
      status: 'unknown',
      route: 'review',
      reason: 'egg_not_detected',
    };
  }

  if (strongVotes >= TEMPORAL_STRONG_REJECT_VOTES) {
    return {
      ...base,
      status: 'rejected',
      route: 'reject',
      reason: 'temporal_strong_crack',
    };
  }

  if (
    evidenceFrames.length >= TEMPORAL_WEAK_REJECT_VOTES &&
    avgCrackConfidence !== null &&
    avgCrackConfidence >= TEMPORAL_WEAK_REJECT_AVG
  ) {
    return {
      ...base,
      status: 'rejected',
      route: 'reject',
      reason: 'temporal_repeated_weak_crack',
    };
  }

  if (
    eggVotes >= TEMPORAL_APPROVED_EGG_VOTES &&
    weakVotes <= TEMPORAL_APPROVED_MAX_WEAK &&
    strongVotes === 0 &&
    veryStrongVotes === 0
  ) {
    return {
      ...base,
      status: 'approved',
      route: 'accept',
      reason: 'temporal_no_crack',
    };
  }

  return {
    ...base,
    status: 'unknown',
    route: 'review',
    reason: 'temporal_ambiguous',
  };
}

/** Helper para tests: construye frame sintético. */
export function makeTestFrame(options: {
  eggDetected: boolean;
  crackConfidence?: number | null;
}): FrameCrackEvidence {
  const confidence = options.crackConfidence ?? null;
  const level = options.eggDetected ? classifyCrackLevel(confidence) : 'none';
  return {
    eggDetected: options.eggDetected,
    strongestCrackConfidence: options.eggDetected ? confidence : null,
    crackLevel: options.eggDetected ? level : 'none',
    primaryEgg: options.eggDetected
      ? {
          confidence: 0.8,
          bbox: { x1: 100, y1: 100, x2: 300, y2: 400 },
          bbox_normalized: { x1: 0.1, y1: 0.05, x2: 0.3, y2: 0.2 },
        }
      : null,
    currentEvidence: null,
  };
}
