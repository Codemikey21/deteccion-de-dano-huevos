import type { DetectionRoute, DetectionStatus, PredictionResponse } from '../types/prediction';

export const STABILIZATION_WINDOW_SIZE = 5;
export const STABILIZATION_VOTE_THRESHOLD = 3;

export interface FrameSnapshot {
  egg_detected: boolean;
  crack_detected: boolean;
}

export interface StabilizedClassification {
  status: DetectionStatus;
  route: DetectionRoute;
  reason: string;
  window: FrameSnapshot[];
  approvedVotes: number;
  rejectedVotes: number;
}

function toFrameSnapshot(prediction: PredictionResponse): FrameSnapshot {
  return {
    egg_detected: prediction.egg_detected,
    crack_detected: prediction.crack_detected,
  };
}

export function formatWindowSnapshot(frame: FrameSnapshot): string {
  const egg = frame.egg_detected ? 'E+' : 'E-';
  const crack = frame.crack_detected ? 'C+' : 'C-';
  return `${egg}${crack}`;
}

/**
 * Estabiliza el estado operativo sobre una ventana deslizante de frames.
 *
 * - 3+ frames con egg=true y crack=false → approved
 * - 3+ frames con egg=true y crack=true → rejected
 * - cualquier otro caso → review (unknown)
 */
export function computeStabilizedClassification(
  window: FrameSnapshot[],
  voteThreshold: number = STABILIZATION_VOTE_THRESHOLD,
): StabilizedClassification {
  const approvedVotes = window.filter(
    (frame) => frame.egg_detected && !frame.crack_detected,
  ).length;
  const rejectedVotes = window.filter(
    (frame) => frame.egg_detected && frame.crack_detected,
  ).length;

  if (approvedVotes >= voteThreshold) {
    return {
      status: 'approved',
      route: 'accept',
      reason: 'stabilized_no_crack',
      window,
      approvedVotes,
      rejectedVotes,
    };
  }

  if (rejectedVotes >= voteThreshold) {
    return {
      status: 'rejected',
      route: 'reject',
      reason: 'stabilized_crack_detected',
      window,
      approvedVotes,
      rejectedVotes,
    };
  }

  return {
    status: 'unknown',
    route: 'review',
    reason: 'stabilized_insufficient_consensus',
    window,
    approvedVotes,
    rejectedVotes,
  };
}

export function appendFrameToWindow(
  currentWindow: FrameSnapshot[],
  prediction: PredictionResponse,
  windowSize: number = STABILIZATION_WINDOW_SIZE,
): FrameSnapshot[] {
  const nextWindow = [...currentWindow, toFrameSnapshot(prediction)];
  if (nextWindow.length <= windowSize) {
    return nextWindow;
  }
  return nextWindow.slice(nextWindow.length - windowSize);
}
