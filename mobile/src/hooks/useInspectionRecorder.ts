import { useCallback, useEffect, useRef, useState } from 'react';

import { saveInspection } from '../services/inspectionStorage';
import type { InspectionStatus } from '../types/inspection';
import { shouldSaveInspection } from '../utils/inspectionCooldown';

/** Ventana mínima entre guardados del mismo huevo mientras Auto Scan sigue infiriendo. */
const INSPECTION_COOLDOWN_MS = 6000;

export interface RecordInspectionInput {
  status: InspectionStatus;
  crackDetected: boolean;
  eggConfidence?: number;
  crackConfidence?: number;
  inferenceMs?: number;
}

/** Incrementa un id de sesión cada vez que aparece un huevo nuevo (transición null → tracked). */
export function useEggSessionId(hasTrackedEgg: boolean): number {
  const sessionIdRef = useRef(0);
  const wasTrackedRef = useRef(false);
  const [sessionId, setSessionId] = useState(0);

  useEffect(() => {
    if (hasTrackedEgg && !wasTrackedRef.current) {
      sessionIdRef.current += 1;
      setSessionId(sessionIdRef.current);
    }
    wasTrackedRef.current = hasTrackedEgg;
  }, [hasTrackedEgg]);

  return sessionId;
}

export function useInspectionRecorder(sessionId: number): {
  recordIfNeeded: (input: RecordInspectionInput) => void;
} {
  const lastSavedAtRef = useRef<number | null>(null);
  const lastSavedSessionIdRef = useRef<number | null>(null);
  const savingRef = useRef(false);

  const recordIfNeeded = useCallback(
    (input: RecordInspectionInput) => {
      if (savingRef.current) {
        return;
      }

      const now = Date.now();
      const shouldSave = shouldSaveInspection({
        sessionId,
        lastSavedSessionId: lastSavedSessionIdRef.current,
        now,
        lastSavedAt: lastSavedAtRef.current,
        cooldownMs: INSPECTION_COOLDOWN_MS,
      });

      if (!shouldSave) {
        return;
      }

      savingRef.current = true;
      lastSavedAtRef.current = now;
      lastSavedSessionIdRef.current = sessionId;

      void saveInspection(input)
        .catch(() => {
          lastSavedAtRef.current = null;
          lastSavedSessionIdRef.current = null;
        })
        .finally(() => {
          savingRef.current = false;
        });
    },
    [sessionId],
  );

  return { recordIfNeeded };
}
