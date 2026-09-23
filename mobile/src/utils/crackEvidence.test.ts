import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import type { Detection, PredictionResponse } from '../types/prediction';
import {
  buildFrameFromPrediction,
  computeTemporalCrackDecision,
  getCrackEvidenceForPrimaryEgg,
  getCracksForPrimaryEgg,
  makeTestFrame,
} from './crackEvidence';

function prediction(options: {
  egg?: { confidence: number; bbox?: Detection['bbox'] } | null;
  cracks?: Detection[];
}): PredictionResponse {
  const bbox = options.egg?.bbox ?? { x1: 100, y1: 100, x2: 300, y2: 400 };
  return {
    status: 'unknown',
    route: 'review',
    reason: 'egg_not_detected',
    egg_detected: Boolean(options.egg),
    crack_detected: false,
    image: { width: 1000, height: 2000 },
    primary_egg: options.egg
      ? {
          confidence: options.egg.confidence,
          bbox,
          bbox_normalized: {
            x1: bbox.x1 / 1000,
            y1: bbox.y1 / 2000,
            x2: bbox.x2 / 1000,
            y2: bbox.y2 / 2000,
          },
        }
      : null,
    cracks: options.cracks ?? [],
    raw_detections: [],
    detections: [],
    inference_ms: 10,
    model: { name: 'yolov8n', imgsz: 960 },
  };
}

function crack(confidence: number, bbox = { x1: 180, y1: 220, x2: 220, y2: 260 }): Detection {
  return {
    class_id: 1,
    class_name: 'crack',
    confidence,
    bbox,
    bbox_normalized: {
      x1: bbox.x1 / 1000,
      y1: bbox.y1 / 2000,
      x2: bbox.x2 / 1000,
      y2: bbox.y2 / 2000,
    },
  };
}

describe('computeTemporalCrackDecision', () => {
  it('12. crack 0.74 inside egg rejects immediately', () => {
    const frame = buildFrameFromPrediction(
      prediction({ egg: { confidence: 0.78 }, cracks: [crack(0.74)] }),
    );
    const decision = computeTemporalCrackDecision([frame]);
    assert.equal(decision.status, 'rejected');
    assert.equal(decision.reason, 'very_strong_crack');
  });

  it('13. repeated weak cracks reject', () => {
    const window = [
      makeTestFrame({ eggDetected: true, crackConfidence: 0.34 }),
      makeTestFrame({ eggDetected: true, crackConfidence: 0.36 }),
      makeTestFrame({ eggDetected: true, crackConfidence: 0.38 }),
    ];
    const decision = computeTemporalCrackDecision(window);
    assert.equal(decision.status, 'rejected');
    assert.equal(decision.reason, 'temporal_repeated_weak_crack');
  });

  it('14. isolated weak crack does not reject', () => {
    const window = [
      makeTestFrame({ eggDetected: true, crackConfidence: 0.31 }),
      makeTestFrame({ eggDetected: true, crackConfidence: null }),
      makeTestFrame({ eggDetected: true, crackConfidence: null }),
      makeTestFrame({ eggDetected: true, crackConfidence: null }),
      makeTestFrame({ eggDetected: true, crackConfidence: null }),
    ];
    const decision = computeTemporalCrackDecision(window);
    assert.equal(decision.status, 'approved');
  });

  it('very strong persists after frames without egg', () => {
    const window = [
      makeTestFrame({ eggDetected: true, crackConfidence: 0.74 }),
      makeTestFrame({ eggDetected: false, crackConfidence: null }),
      makeTestFrame({ eggDetected: false, crackConfidence: null }),
    ];
    const decision = computeTemporalCrackDecision(window);
    assert.equal(decision.status, 'rejected');
    assert.equal(decision.reason, 'very_strong_crack');
  });

  it('two strong cracks reject', () => {
    const window = [
      makeTestFrame({ eggDetected: true, crackConfidence: 0.6 }),
      makeTestFrame({ eggDetected: true, crackConfidence: 0.58 }),
    ];
    const decision = computeTemporalCrackDecision(window);
    assert.equal(decision.status, 'rejected');
    assert.equal(decision.reason, 'temporal_strong_crack');
  });
});

describe('buildFrameFromPrediction', () => {
  it('uses backend primary_egg as source of truth', () => {
    const frame = buildFrameFromPrediction(
      prediction({ egg: { confidence: 0.87 } }),
    );
    assert.equal(frame.primaryEgg?.confidence, 0.87);
    assert.equal(frame.eggDetected, true);
  });

  it('11. ignores cracks not associated by backend', () => {
    const frame = buildFrameFromPrediction(
      prediction({ egg: { confidence: 0.9 }, cracks: [] }),
    );
    assert.equal(frame.crackLevel, 'none');
  });
});

describe('getCrackEvidenceForPrimaryEgg', () => {
  it('detects very strong associated crack', () => {
    const evidence = getCrackEvidenceForPrimaryEgg([crack(0.74)]);
    assert.equal(evidence.level, 'very_strong');
    assert.equal(evidence.representativeCrack?.confidence, 0.74);
  });
});

describe('getCracksForPrimaryEgg', () => {
  it('returns backend associated cracks only', () => {
    const cracks = getCracksForPrimaryEgg(
      prediction({ egg: { confidence: 0.8 }, cracks: [crack(0.62)] }),
    );
    assert.equal(cracks.length, 1);
  });
});
