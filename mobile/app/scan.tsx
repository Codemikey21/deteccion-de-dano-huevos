import { CameraView, useCameraPermissions } from 'expo-camera';
import { useCallback, useRef, useState } from 'react';
import {
  ActivityIndicator,
  LayoutChangeEvent,
  Pressable,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';

import { DetectionOverlay } from '../src/components/DetectionOverlay';
import { useAutoScan } from '../src/hooks/useAutoScan';
import { useStabilizedClassification } from '../src/hooks/useStabilizedClassification';
import type { PreviewSize } from '../src/utils/bbox';

function scanStatusLabel(options: {
  cameraReady: boolean;
  autoScanEnabled: boolean;
  isProcessing: boolean;
  hasPrediction: boolean;
}): string {
  if (!options.cameraReady) {
    return 'Initializing camera…';
  }
  if (!options.autoScanEnabled) {
    return 'Ready';
  }
  if (options.isProcessing && !options.hasPrediction) {
    return 'Processing…';
  }
  if (!options.hasPrediction) {
    return 'Waiting';
  }
  return 'Active';
}

export default function ScanScreen() {
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

  const { stabilized, windowLabel } = useStabilizedClassification(
    prediction,
    autoScanEnabled,
  );

  const handlePreviewLayout = useCallback((event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setPreviewSize({ width, height });
  }, []);

  if (!permission) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
        <Text style={styles.message}>Verificando permisos de cámara…</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.centered}>
        <Text style={styles.title}>Permiso de cámara requerido</Text>
        <Text style={styles.message}>
          La detección en vivo necesita acceso a la cámara trasera del dispositivo.
        </Text>
        <Pressable style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Conceder permiso</Text>
        </Pressable>
      </View>
    );
  }

  const statusLabel = scanStatusLabel({
    cameraReady,
    autoScanEnabled,
    isProcessing,
    hasPrediction: prediction !== null,
  });

  return (
    <View style={styles.container}>
      <View style={styles.preview} onLayout={handlePreviewLayout}>
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

        {prediction && previewSize.width > 0 ? (
          <DetectionOverlay
            detections={prediction.detections}
            imageWidth={prediction.image.width}
            imageHeight={prediction.image.height}
            preview={previewSize}
          />
        ) : null}
      </View>

      <View style={styles.debugPanel}>
        <View style={styles.switchRow}>
          <Text style={styles.debugTitle}>Auto Scan</Text>
          <Switch
            value={autoScanEnabled}
            onValueChange={setAutoScanEnabled}
            disabled={!cameraReady}
          />
          <Text style={styles.switchLabel}>{autoScanEnabled ? 'ON' : 'OFF'}</Text>
        </View>

        <Text style={styles.debugLine}>Status: {statusLabel}</Text>
        <Text style={styles.debugLine}>
          cameraReady: {String(cameraReady)} · isProcessing: {String(isProcessing)}
        </Text>

        {prediction ? (
          <>
            <Text style={styles.debugLine}>detections: {prediction.detections.length}</Text>
            <Text style={styles.debugLine}>egg_detected: {String(prediction.egg_detected)}</Text>
            <Text style={styles.debugLine}>
              crack_detected: {String(prediction.crack_detected)}
            </Text>
            <Text style={styles.debugLine}>raw status: {prediction.status}</Text>
            <Text style={styles.debugLine}>raw reason: {prediction.reason}</Text>
            <Text style={styles.debugLine}>
              stabilized status: {stabilized?.status ?? 'pending'}
            </Text>
            <Text style={styles.debugLine}>
              stabilized route: {stabilized?.route ?? 'pending'}
            </Text>
            <Text style={styles.debugLine} numberOfLines={2}>
              window: {windowLabel || 'empty'}
            </Text>
            <Text style={styles.debugLine}>
              votes: approved={stabilized?.approvedVotes ?? 0} rejected=
              {stabilized?.rejectedVotes ?? 0}
            </Text>
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
            capture {metrics.captureMs}ms · cycle {metrics.cycleMs}ms
          </Text>
        ) : null}

        {cameraError ? <Text style={styles.errorText}>Camera: {cameraError}</Text> : null}
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  preview: {
    flex: 1,
    overflow: 'hidden',
  },
  debugPanel: {
    padding: 14,
    gap: 4,
    backgroundColor: 'rgba(0,0,0,0.75)',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 4,
  },
  debugTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
    flex: 1,
  },
  switchLabel: {
    color: '#ccc',
    fontSize: 12,
    fontWeight: '600',
    width: 28,
  },
  debugLine: {
    color: '#ddd',
    fontSize: 12,
  },
  debugMeta: {
    color: '#aaa',
    fontSize: 11,
    marginTop: 2,
  },
  errorText: {
    color: '#ffb4b4',
    fontSize: 12,
    marginTop: 4,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    gap: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
  },
  message: {
    fontSize: 14,
    lineHeight: 20,
    color: '#444',
    textAlign: 'center',
  },
  button: {
    alignSelf: 'center',
    backgroundColor: '#111',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
