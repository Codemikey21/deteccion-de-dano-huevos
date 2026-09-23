import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import {
  detectOrientationFix,
  mapNormalizedBboxToPreview,
  normalizedAreaRatio,
  rotateNormalizedBBox90CW,
} from './bboxTransform';

describe('bboxTransform', () => {
  it('1. central egg maps to central preview region', () => {
    const mapped = mapNormalizedBboxToPreview(
      { x1: 0.35, y1: 0.35, x2: 0.65, y2: 0.65 },
      1000,
      2000,
      { width: 390, height: 844 },
      'none',
    );

    const centerX = (mapped.x1 + mapped.x2) / 2;
    const centerY = (mapped.y1 + mapped.y2) / 2;
    assert.ok(centerX > 390 * 0.3 && centerX < 390 * 0.7);
    assert.ok(centerY > 844 * 0.3 && centerY < 844 * 0.7);
  });

  it('2. small bbox never becomes giant after mapping', () => {
    const small = { x1: 0.45, y1: 0.45, x2: 0.55, y2: 0.55 };
    const mapped = mapNormalizedBboxToPreview(
      small,
      1000,
      2000,
      { width: 390, height: 844 },
      'none',
    );

    const mappedAreaRatio =
      (mapped.width * mapped.height) / (390 * 844);
    assert.ok(mappedAreaRatio < 0.2);
    assert.ok(normalizedAreaRatio(small) < 0.02);
  });

  it('3. portrait source to portrait preview', () => {
    const fix = detectOrientationFix(1000, 2000, 390, 844);
    assert.equal(fix, 'none');
  });

  it('4. landscape source to portrait preview uses rotation', () => {
    const fix = detectOrientationFix(2000, 1000, 390, 844);
    assert.equal(fix, 'rotate90cw');
  });

  it('5. horizontal crop is applied for cover mapping', () => {
    const mapped = mapNormalizedBboxToPreview(
      { x1: 0, y1: 0, x2: 1, y2: 1 },
      1000,
      2000,
      { width: 390, height: 844 },
      'none',
    );

    assert.ok(mapped.width >= 390 * 0.95);
    assert.ok(mapped.height >= 844 * 0.95);
  });

  it('6. vertical crop scenario keeps bbox inside preview', () => {
    const mapped = mapNormalizedBboxToPreview(
      { x1: 0.2, y1: 0.2, x2: 0.8, y2: 0.8 },
      2000,
      1000,
      { width: 390, height: 844 },
      'rotate90cw',
    );

    assert.ok(mapped.x1 >= -5);
    assert.ok(mapped.y1 >= -5);
    assert.ok(mapped.x2 <= 395);
    assert.ok(mapped.y2 <= 849);
  });

  it('rotation preserves area order of magnitude', () => {
    const original = { x1: 0.3, y1: 0.3, x2: 0.7, y2: 0.7 };
    const rotated = rotateNormalizedBBox90CW(original);
    const ratio = normalizedAreaRatio(rotated) / normalizedAreaRatio(original);
    assert.ok(ratio > 0.8 && ratio < 1.2);
  });
});
