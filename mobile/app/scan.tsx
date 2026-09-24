import { CameraView, useCameraPermissions } from 'expo-camera';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  LayoutChangeEvent,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { DetectionOverlay } from '../src/components/DetectionOverlay';
import { InspectionZone } from '../src/components/InspectionZone';
import { StatusCard } from '../src/components/StatusCard';
import { SHOW_DEBUG } from '../src/constants/debug';
import { colors, radius, spacing } from '../src/constants/theme';
import { useAutoScan } from '../src/hooks/useAutoScan';
import { useEggVision } from '../src/hooks/useEggVision';
import { useEggSessionId, useInspectionRecorder } from '../src/hooks/useInspectionRecorder';
import type { PreviewSize } from '../src/utils/bboxTransform';
import { formatDetectionsSummary } from '../src/utils/formatDetections';
import { resolvePrimaryEgg } from '../src/utils/resolvePrimaryEgg';

export default function ScanScreen() {
  const insets = useSafeAreaInsets();
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [previewSize, setPreviewSize] = useState<PreviewSize>({ width: 0, height: 0 });

  const {
    autoScanEnabled,
    setAutoScanEnabled,
    isProcessing,
    prediction,
    error,
    lastInferenceMs,
    metrics,
  } = useAutoScan({
    cameraRef,
    cameraReady,
  });

  const {
    trackedEgg,
    temporal,
    temporalCracksLabel,
    displayStatus,
    crackEvidence,
    visualBoxes,
    bboxDebug,
    associatedCracks,
  } = useEggVision(prediction, previewSize, autoScanEnabled);

  const sessionId = useEggSessionId(trackedEgg !== null);
  const { recordIfNeeded } = useInspectionRecorder(sessionId);

  useEffect(() => {
    if (displayStatus !== 'approved' && displayStatus !== 'rejected') {
      return;
    }

    recordIfNeeded({
      status: displayStatus,
      crackDetected: (crackEvidence?.level ?? 'none') !== 'none',
      eggConfidence: trackedEgg?.egg.confidence,
      crackConfidence: crackEvidence?.strongestConfidence ?? undefined,
      inferenceMs: lastInferenceMs ?? prediction?.inference_ms,
    });
  }, [displayStatus, recordIfNeeded, crackEvidence, trackedEgg, lastInferenceMs, prediction]);

  const handlePreviewLayout = useCallback((event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setPreviewSize({ width, height });
  }, []);

  const resolvedPrimaryEgg = prediction ? resolvePrimaryEgg(prediction) : null;

  const hasResult = displayStatus === 'approved' || displayStatus === 'rejected';
  const crackDetected = (crackEvidence?.level ?? 'none') !== 'none';
  const inferenceMsToShow = lastInferenceMs ?? prediction?.inference_ms ?? null;

  const connectionNotice = useMemo(() => {
    if (cameraError) {
      return 'No se pudo iniciar la cámara.';
    }
    if (error) {
      return 'Problema de conexión con el servidor. Reintentando…';
    }
    return null;
  }, [cameraError, error]);

  if (!permission) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.graphite} />
        <Text style={styles.message}>Verificando permisos de cámara…</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.centered}>
        <Text style={styles.permissionTitle}>Permiso de cámara requerido</Text>
        <Text style={styles.message}>
          La detección en vivo necesita acceso a la cámara trasera del dispositivo.
        </Text>
        <Pressable style={styles.permissionButton} onPress={requestPermission}>
          <Text style={styles.permissionButtonText}>Conceder permiso</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>EggVision</Text>
        <View style={styles.systemIndicator}>
          <View
            style={[
              styles.systemDot,
              { backgroundColor: cameraReady ? colors.olive : colors.textSecondary },
            ]}
          />
          <Text style={styles.systemText}>Sistema activo</Text>
        </View>
      </View>

      <View style={styles.cameraCard} onLayout={handlePreviewLayout}>
        <CameraView
          ref={cameraRef}
          style={StyleSheet.absoluteFill}
          facing="back"
          onCameraReady={() => {
            setCameraReady(true);
            setCameraError(null);
          }}
          onMountError={(event) => {
            setCameraReady(false);
            setCameraError(event.message);
          }}
        />

        <InspectionZone status={displayStatus} />

        {SHOW_DEBUG ? (
          <DetectionOverlay visualBoxes={visualBoxes} preview={previewSize} />
        ) : null}
      </View>

      <ScrollView
        style={styles.sheet}
        contentContainerStyle={[styles.sheetContent, { paddingBottom: insets.bottom + spacing.lg }]}
      >
        <StatusCard status={displayStatus} />

        {hasResult ? (
          <View style={styles.secondaryInfo}>
            <Text style={styles.secondaryLine}>Huevo detectado</Text>
            <Text style={styles.secondaryLine}>
              Grieta: {crackDetected ? 'detectada' : 'no detectada'}
            </Text>
            {inferenceMsToShow !== null ? (
              <Text style={styles.secondaryLine}>Tiempo de análisis: {inferenceMsToShow} ms</Text>
            ) : null}
          </View>
        ) : null}

        <View style={styles.switchRow}>
          <View>
            <Text style={styles.switchTitle}>Auto Scan</Text>
            <Text style={styles.switchHint}>
              {autoScanEnabled ? 'Analizando automáticamente' : 'Detenido'}
            </Text>
          </View>
          <Switch
            value={autoScanEnabled}
            onValueChange={setAutoScanEnabled}
            disabled={!cameraReady}
            trackColor={{ false: colors.border, true: colors.oliveSoft }}
            thumbColor={autoScanEnabled ? colors.olive : colors.surface}
          />
        </View>

        {connectionNotice ? <Text style={styles.notice}>{connectionNotice}</Text> : null}

        {SHOW_DEBUG ? (
          <View style={styles.debugPanel}>
            <Text style={styles.debugTitle}>Panel técnico</Text>
            <Text style={styles.debugLine}>displayStatus: {displayStatus}</Text>
            <Text style={styles.debugLine}>
              cameraReady: {String(cameraReady)} · isProcessing: {String(isProcessing)}
            </Text>

            {prediction ? (
              <>
                <Text style={styles.debugLine}>
                  primary egg: {resolvedPrimaryEgg?.confidence.toFixed(2) ?? 'none'}
                </Text>
                <Text style={styles.debugLine}>
                  egg tracker: {trackedEgg?.phase ?? 'none'} · missed:{' '}
                  {trackedEgg?.missedFrames ?? 0}
                  {trackedEgg?.outlierRejected ? ' · outlier' : ''}
                  {trackedEgg?.modelLocalizationError ? ' · MODEL_LOCALIZATION_ERROR' : ''}
                </Text>
                <Text style={styles.debugLine}>
                  raw detections ({prediction.raw_detections?.length ?? 0}):{' '}
                  {formatDetectionsSummary(prediction.raw_detections)}
                </Text>
                <Text style={styles.debugLine}>
                  associated cracks ({associatedCracks.length}):{' '}
                  {formatDetectionsSummary(associatedCracks)}
                </Text>
                <Text style={styles.debugLine} numberOfLines={2}>
                  temporal window: {temporalCracksLabel || 'empty'}
                </Text>
                <Text style={styles.debugLine}>
                  weak: {temporal?.weakVotes ?? 0} · strong: {temporal?.strongVotes ?? 0} · very
                  strong: {temporal?.veryStrongVotes ?? 0}
                </Text>
                <Text style={styles.debugLine}>raw status: {prediction.status}</Text>
                <Text style={styles.debugLine}>
                  temporal reason: {temporal?.reason ?? 'pending'}
                </Text>

                {bboxDebug ? (
                  <>
                    <Text style={styles.debugLine}>
                      source: {bboxDebug.sourceWidth}x{bboxDebug.sourceHeight} · preview:{' '}
                      {bboxDebug.previewWidth}x{bboxDebug.previewHeight}
                    </Text>
                    <Text style={styles.debugLine}>
                      orientation: {bboxDebug.orientationFix} · area ratio:{' '}
                      {bboxDebug.areaRatio.toFixed(3)}
                    </Text>
                  </>
                ) : null}

                <Text style={styles.debugLine}>
                  inference_ms: {lastInferenceMs ?? prediction.inference_ms}
                </Text>
              </>
            ) : (
              <Text style={styles.debugLine}>
                {autoScanEnabled ? 'Esperando primera inferencia…' : 'Activa Auto Scan para inferir'}
              </Text>
            )}

            {metrics ? (
              <Text style={styles.debugMeta}>
                capture {metrics.captureMs}ms · preprocess {metrics.preprocessMs}ms · network{' '}
                {metrics.uploadNetworkMs.toFixed(0)}ms · inference {metrics.serverInferenceMs}ms ·
                cycle {metrics.cycleMs}ms
                {metrics.resized ? ' · resized' : ''}
              </Text>
            ) : null}

            {cameraError ? <Text style={styles.errorText}>Camera: {cameraError}</Text> : null}
            {error ? <Text style={styles.errorText}>{error}</Text> : null}
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    paddingBottom: spacing.md,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  systemIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  systemDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  systemText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  cameraCard: {
    marginHorizontal: spacing.lg,
    height: '42%',
    borderRadius: radius.lg,
    overflow: 'hidden',
    backgroundColor: colors.graphite,
  },
  sheet: {
    flex: 1,
  },
  sheetContent: {
    padding: spacing.lg,
    gap: spacing.md,
  },
  secondaryInfo: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: 4,
  },
  secondaryLine: {
    fontSize: 13,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  switchTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  switchHint: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  notice: {
    fontSize: 12,
    color: colors.terracottaStrong,
    textAlign: 'center',
  },
  debugPanel: {
    marginTop: spacing.sm,
    padding: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.graphite,
    gap: 4,
  },
  debugTitle: {
    color: colors.textInverse,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 4,
  },
  debugLine: {
    color: '#ddd',
    fontSize: 11,
  },
  debugMeta: {
    color: '#aaa',
    fontSize: 10,
    marginTop: 2,
  },
  errorText: {
    color: '#ffb4b4',
    fontSize: 11,
    marginTop: 4,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
    gap: spacing.md,
    backgroundColor: colors.background,
  },
  permissionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textPrimary,
    textAlign: 'center',
  },
  message: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  permissionButton: {
    alignSelf: 'center',
    backgroundColor: colors.graphite,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: radius.sm,
    marginTop: 8,
  },
  permissionButtonText: {
    color: colors.textInverse,
    fontWeight: '600',
  },
});
