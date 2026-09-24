import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { shouldSaveInspection } from './inspectionCooldown';

describe('shouldSaveInspection', () => {
  it('saves the first inspection when nothing was saved before', () => {
    const result = shouldSaveInspection({
      sessionId: 1,
      lastSavedSessionId: null,
      now: 1000,
      lastSavedAt: null,
      cooldownMs: 6000,
    });
    assert.equal(result, true);
  });

  it('saves when the egg session changed even if cooldown has not elapsed', () => {
    const result = shouldSaveInspection({
      sessionId: 2,
      lastSavedSessionId: 1,
      now: 1000,
      lastSavedAt: 900,
      cooldownMs: 6000,
    });
    assert.equal(result, true);
  });

  it('does not save the same session again before cooldown elapses', () => {
    const result = shouldSaveInspection({
      sessionId: 1,
      lastSavedSessionId: 1,
      now: 3000,
      lastSavedAt: 0,
      cooldownMs: 6000,
    });
    assert.equal(result, false);
  });

  it('saves the same session again once cooldown elapses', () => {
    const result = shouldSaveInspection({
      sessionId: 1,
      lastSavedSessionId: 1,
      now: 6000,
      lastSavedAt: 0,
      cooldownMs: 6000,
    });
    assert.equal(result, true);
  });
});
