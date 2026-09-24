import AsyncStorage from '@react-native-async-storage/async-storage';

import type { Inspection, InspectionStats } from '../types/inspection';

const STORAGE_KEY = 'eggvision.inspections.v1';
const MAX_STORED_INSPECTIONS = 500;

type Listener = (inspections: Inspection[]) => void;

const listeners = new Set<Listener>();

function notify(inspections: Inspection[]): void {
  for (const listener of listeners) {
    listener(inspections);
  }
}

export function subscribeToInspections(listener: Listener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function generateId(): string {
  return `insp_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export async function getInspections(): Promise<Inspection[]> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Inspection[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed;
  } catch {
    return [];
  }
}

export async function saveInspection(
  input: Omit<Inspection, 'id' | 'timestamp'>,
): Promise<Inspection> {
  const inspection: Inspection = {
    ...input,
    id: generateId(),
    timestamp: new Date().toISOString(),
  };

  const current = await getInspections();
  const next = [inspection, ...current].slice(0, MAX_STORED_INSPECTIONS);

  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  notify(next);

  return inspection;
}

export async function clearInspections(): Promise<void> {
  await AsyncStorage.removeItem(STORAGE_KEY);
  notify([]);
}

export function computeInspectionStats(inspections: Inspection[]): InspectionStats {
  const total = inspections.length;
  const approved = inspections.filter((item) => item.status === 'approved').length;
  const rejected = total - approved;

  const withInference = inspections.filter((item) => typeof item.inferenceMs === 'number');
  const avgInferenceMs =
    withInference.length > 0
      ? withInference.reduce((sum, item) => sum + (item.inferenceMs ?? 0), 0) /
        withInference.length
      : null;

  return {
    total,
    approved,
    rejected,
    approvedPct: total > 0 ? (approved / total) * 100 : 0,
    rejectedPct: total > 0 ? (rejected / total) * 100 : 0,
    lastInspection: inspections[0] ?? null,
    avgInferenceMs,
  };
}
