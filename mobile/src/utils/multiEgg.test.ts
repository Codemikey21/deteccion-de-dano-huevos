import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import type { EggResult, PredictionResponse } from '../types/prediction';
import { damageLabel, getMultiEggResult } from './multiEgg';

function prediction(eggs?: EggResult[] | null): PredictionResponse {
  return { eggs, status: 'approved', route: 'accept', reason: 'no_crack_detected',
    egg_detected: true, crack_detected: false, image: { width: 100, height: 100 },
    detections: [], inference_ms: 20, model: { name: 'yolov8n', imgsz: 960 } };
}
function egg(id: number, damaged = false): EggResult {
  return { id, status: damaged ? 'damaged' : 'healthy', confidence: 0.9,
    damage_source: damaged ? 'dark_line' : 'none', dark_line_area_ratio: damaged ? 0.02 : 0,
    bbox: { x1: 10, y1: 10, x2: 90, y2: 90 },
    bbox_normalized: { x1: 0.1, y1: 0.1, x2: 0.9, y2: 0.9 }, cracks: [] };
}

describe('multi-egg presentation', () => {
  it('preserves legacy and missing response handling', () => {
    assert.equal(getMultiEggResult(null), null);
    assert.equal(getMultiEggResult(prediction()), null);
    assert.equal(getMultiEggResult(prediction(null)), null);
  });
  it('zero eggs is a valid empty frame, not a legacy response', () => {
    assert.deepEqual(getMultiEggResult(prediction([]))?.summary, { total: 0, healthy: 0, damaged: 0 });
  });
  it('reports one healthy egg', () => {
    assert.deepEqual(getMultiEggResult(prediction([egg(1)]))?.summary, { total: 1, healthy: 1, damaged: 0 });
  });
  it('reports simulated damage even with no YOLO cracks', () => {
    assert.deepEqual(getMultiEggResult(prediction([egg(1, true)]))?.summary, { total: 1, healthy: 0, damaged: 1 });
  });
  it('preserves frame order and summarizes all five independently of primary status', () => {
    const eggs = [egg(1), egg(2, true), egg(3), egg(4, true), egg(5)];
    const result = getMultiEggResult(prediction(eggs));
    assert.deepEqual(result?.summary, { total: 5, healthy: 3, damaged: 2 });
    assert.deepEqual(result?.eggs.map((item) => item.id), [1, 2, 3, 4, 5]);
  });
  it('distinguishes simulated marks from model evidence', () => {
    assert.equal(damageLabel('dark_line'), 'marca oscura visible');
    assert.match(damageLabel('yolo_crack'), /modelo/);
    assert.match(damageLabel('both'), /raya oscura y grieta/);
    assert.equal(damageLabel('none'), 'sin daño visible detectado');
  });
});
