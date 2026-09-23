import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { computeDisplayStatus } from './displayStatus';
import type { TemporalCrackDecision } from './crackEvidence';
import { resetEggTracker, updateEggTracker } from './eggTracker';

function temporal(status: 'approved' | 'rejected' | 'unknown', reason: string): TemporalCrackDecision {
  return {
    status,
    route: status === 'rejected' ? 'reject' : status === 'approved' ? 'accept' : 'review',
    reason,
    window: [],
    strongVotes: 0,
    veryStrongVotes: 0,
    weakVotes: 0,
    eggVotes: 0,
    avgCrackConfidence: null,
  };
}

describe('displayStatus', () => {
  it('15. visual status matches temporal rejection', () => {
    const tracker = resetEggTracker();
    const status = computeDisplayStatus(
      tracker,
      temporal('rejected', 'very_strong_crack'),
      true,
    );
    assert.equal(status, 'rejected');
  });

  it('returns approved when temporal approves', () => {
    const status = computeDisplayStatus(
      resetEggTracker(),
      temporal('approved', 'temporal_no_crack'),
      true,
    );
    assert.equal(status, 'approved');
  });

  it('returns review while egg is tracked but temporal ambiguous', () => {
    let tracker = resetEggTracker();
    tracker = updateEggTracker(tracker, {
      confidence: 0.8,
      bbox: { x1: 0, y1: 0, x2: 1, y2: 1 },
      bbox_normalized: { x1: 0.3, y1: 0.3, x2: 0.7, y2: 0.7 },
    });
    const status = computeDisplayStatus(
      tracker,
      temporal('unknown', 'temporal_ambiguous'),
      true,
    );
    assert.equal(status, 'review');
  });
});
