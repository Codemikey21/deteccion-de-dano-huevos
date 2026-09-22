import { CameraView, useCameraPermissions } from 'expo-camera';
import { useRef } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { useAutoScan } from '../src/hooks/useAutoScan';

export default function ScanScreen() {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();

  const { enabled, setEnabled, isProcessing, lastResult, lastError } = useAutoScan({
    cameraRef,
  });

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

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing="back" />

      <View style={styles.overlay}>
        <Text style={styles.overlayTitle}>Cámara en vivo</Text>
        <Text style={styles.overlayText}>
          Auto-detección preparada. El envío periódico al backend permanece desactivado
          hasta validar el flujo completo.
        </Text>
        <Text style={styles.overlayMeta}>
          Estado: {enabled ? 'activo (dev)' : 'inactivo'} ·{' '}
          {isProcessing ? 'procesando…' : 'en espera'}
        </Text>
        {lastResult ? (
          <Text style={styles.overlayMeta}>
            Última respuesta: {lastResult.status} ({lastResult.detections.length}{' '}
            detecciones)
          </Text>
        ) : null}
        {lastError ? <Text style={styles.errorText}>{lastError}</Text> : null}

        <Pressable
          style={[styles.button, enabled && styles.buttonActive]}
          onPress={() => setEnabled((current) => !current)}
        >
          <Text style={styles.buttonText}>
            {enabled ? 'Desactivar auto-scan (dev)' : 'Activar auto-scan (dev)'}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    padding: 16,
    gap: 8,
    backgroundColor: 'rgba(0,0,0,0.55)',
  },
  overlayTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  overlayText: {
    color: '#eee',
    fontSize: 13,
    lineHeight: 18,
  },
  overlayMeta: {
    color: '#ccc',
    fontSize: 12,
  },
  errorText: {
    color: '#ffb4b4',
    fontSize: 12,
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
    alignSelf: 'flex-start',
    backgroundColor: '#111',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonActive: {
    backgroundColor: '#333',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
