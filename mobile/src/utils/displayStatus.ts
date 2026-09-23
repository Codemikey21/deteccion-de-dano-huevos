import type { DisplayStatus } from '../types/prediction';
import type { TemporalCrackDecision } from './crackEvidence';
import type { EggTrackerState } from './eggTracker';

export function computeDisplayStatus(
  tracker: EggTrackerState,
  temporal: TemporalCrackDecision | null,
  autoScanEnabled: boolean,
): DisplayStatus {
  if (!autoScanEnabled) {
    return 'detecting';
  }

  if (temporal?.status === 'rejected') {
    return 'rejected';
  }

  if (temporal?.status === 'approved') {
    return 'approved';
  }

  if (tracker.tracked) {
    return 'review';
  }

  if (temporal?.status === 'unknown') {
    return tracker.tracked ? 'review' : 'detecting';
  }

  return 'detecting';
}
