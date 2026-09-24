/**
 * Cooldown para evitar guardar el mismo huevo repetidas veces mientras
 * Auto Scan sigue infiriendo sobre el mismo huevo ya resuelto.
 * Guarda solo si cambia la sesión de huevo (nuevo trackedEgg) o si pasó
 * el cooldown desde el último guardado.
 */
export function shouldSaveInspection(options: {
  sessionId: number;
  lastSavedSessionId: number | null;
  now: number;
  lastSavedAt: number | null;
  cooldownMs: number;
}): boolean {
  const { sessionId, lastSavedSessionId, now, lastSavedAt, cooldownMs } = options;

  if (lastSavedSessionId === null || lastSavedAt === null) {
    return true;
  }

  if (sessionId !== lastSavedSessionId) {
    return true;
  }

  return now - lastSavedAt >= cooldownMs;
}
