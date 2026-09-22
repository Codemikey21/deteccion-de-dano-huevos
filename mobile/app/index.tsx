import { Link } from 'expo-router';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { BackendConnectionDev } from '../src/components/BackendConnectionDev';

export default function HomeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>EggVision</Text>
      <Text style={styles.subtitle}>
        Base técnica del frontend móvil. El diseño final se implementará en una fase
        posterior.
      </Text>
      <Link href="/scan" style={styles.button}>
        <Text style={styles.buttonText}>Ir a Scan</Text>
      </Link>

      <BackendConnectionDev />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
    gap: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: '#444',
  },
  button: {
    alignSelf: 'flex-start',
    backgroundColor: '#111',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
