import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { API_BASE_URL } from '../constants/config';
import { healthCheck } from '../services/api';
import type { HealthResponse } from '../types/prediction';

type ConnectionState = 'idle' | 'checking' | 'connected' | 'error';

export function BackendConnectionDev() {
  const [state, setState] = useState<ConnectionState>('idle');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const runHealthCheck = useCallback(async () => {
    if (!API_BASE_URL) {
      setState('error');
      setHealth(null);
      setErrorMessage('EXPO_PUBLIC_API_URL no está configurada en mobile/.env');
      return;
    }

    setState('checking');
    setHealth(null);
    setErrorMessage(null);

    try {
      const response = await healthCheck();
      setHealth(response);
      setState('connected');
    } catch (error) {
      setState('error');
      setErrorMessage(error instanceof Error ? error.message : 'Error desconocido');
    }
  }, []);

  const statusLabel =
    state === 'checking'
      ? 'Checking...'
      : state === 'connected'
        ? 'Connected'
        : state === 'error'
          ? 'Error'
          : 'Idle';

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Backend (dev)</Text>
      <Text style={styles.line}>Backend: {statusLabel}</Text>
      {API_BASE_URL ? (
        <Text style={styles.meta} numberOfLines={1}>
          URL: {API_BASE_URL}
        </Text>
      ) : (
        <Text style={styles.error}>URL no configurada</Text>
      )}

      {state === 'checking' ? <ActivityIndicator style={styles.spinner} /> : null}

      {state === 'connected' && health ? (
        <View style={styles.details}>
          <Text style={styles.meta}>model_loaded: {String(health.model_loaded)}</Text>
          <Text style={styles.meta}>model: {health.model}</Text>
          <Text style={styles.meta}>input_size: {health.input_size}</Text>
        </View>
      ) : null}

      {state === 'error' && errorMessage ? (
        <Text style={styles.error}>{errorMessage}</Text>
      ) : null}

      <Pressable
        style={[styles.button, state === 'checking' && styles.buttonDisabled]}
        onPress={() => void runHealthCheck()}
        disabled={state === 'checking'}
      >
        <Text style={styles.buttonText}>Test AWS connection</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 24,
    padding: 16,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    gap: 6,
  },
  heading: {
    fontSize: 14,
    fontWeight: '700',
    color: '#666',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  line: {
    fontSize: 15,
    fontWeight: '600',
  },
  meta: {
    fontSize: 13,
    color: '#555',
  },
  details: {
    gap: 2,
    marginTop: 4,
  },
  error: {
    fontSize: 13,
    color: '#b00020',
  },
  spinner: {
    marginTop: 4,
  },
  button: {
    alignSelf: 'flex-start',
    backgroundColor: '#333',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 13,
  },
});
