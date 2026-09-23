import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import type { PrimaryEgg } from '../types/prediction';
import { resetEggTracker, updateEggTracker } from './eggTracker';

function egg(
  confidence: number,
  bbox_normalized = { x1: 0.3, y1: 0.3, x2: 0.7, y2: 0.7 },
): PrimaryEgg {
  return {
    confidence,
    bbox: { x1: 300, y1: 600, x2: 700, y2: 1400 },
    bbox_normalized,
  };
}

describe('eggTracker', () => {
  it('7. one missed frame keeps lastValidEgg', () => {
    let state = resetEggTracker();
    state = updateEggTracker(state, egg(0.9));
    state = updateEggTracker(state, null);
    assert.ok(state.tracked);
    assert.equal(state.tracked?.phase, 'persisted');
    assert.equal(state.tracked?.missedFrames, 1);
  });

  it('8. three missed frames clear tracker', () => {
    let state = resetEggTracker();
    state = updateEggTracker(state, egg(0.9));
    state = updateEggTracker(state, null);
    state = updateEggTracker(state, null);
    state = updateEggTracker(state, null);
    assert.equal(state.tracked, null);
  });

  it('rejects absurd spatial outlier and keeps previous bbox briefly', () => {
    let state = resetEggTracker();
    state = updateEggTracker(state, egg(0.9, { x1: 0.35, y1: 0.35, x2: 0.65, y2: 0.65 }));
    state = updateEggTracker(
      state,
      egg(0.95, { x1: 0.0, y1: 0.0, x2: 0.98, y2: 0.98 }),
    );
    assert.ok(state.tracked);
    assert.equal(state.tracked?.outlierRejected, true);
    assert.equal(state.tracked?.egg.confidence, 0.9);
  });

  it('updates tracker when new egg is spatially consistent', () => {
    let state = resetEggTracker();
    state = updateEggTracker(state, egg(0.8));
    state = updateEggTracker(state, egg(0.85, { x1: 0.32, y1: 0.32, x2: 0.68, y2: 0.68 }));
    assert.equal(state.tracked?.egg.confidence, 0.85);
    assert.equal(state.tracked?.missedFrames, 0);
  });
});
