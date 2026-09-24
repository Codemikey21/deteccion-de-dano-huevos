import { Link } from 'expo-router';
import { useMemo } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { BackendConnectionDev } from '../src/components/BackendConnectionDev';
import { StatTile } from '../src/components/StatTile';
import { SHOW_DEBUG } from '../src/constants/debug';
import { colors, radius, spacing } from '../src/constants/theme';
import { useInspections } from '../src/hooks/useInspections';

function isSameDay(iso: string, reference: Date): boolean {
  const date = new Date(iso);
  return (
    date.getFullYear() === reference.getFullYear() &&
    date.getMonth() === reference.getMonth() &&
    date.getDate() === reference.getDate()
  );
}

export default function HomeScreen() {
  const { inspections } = useInspections();

  const todayStats = useMemo(() => {
    const today = new Date();
    const todayInspections = inspections.filter((item) => isSameDay(item.timestamp, today));
    const approved = todayInspections.filter((item) => item.status === 'approved').length;
    const rejected = todayInspections.length - approved;
    return { total: todayInspections.length, approved, rejected };
  }, [inspections]);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>EggVision</Text>
        <Text style={styles.subtitle}>Inspección inteligente de huevos</Text>
      </View>

      <Link href="/scan" asChild>
        <Pressable style={styles.primaryCard}>
          <Text style={styles.primaryCardLabel}>Iniciar inspección</Text>
          <Text style={styles.primaryCardHint}>Abrir cámara y comenzar Auto Scan</Text>
        </Pressable>
      </Link>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Resumen del día</Text>
        <View style={styles.statsRow}>
          <StatTile label="Inspecciones" value={String(todayStats.total)} />
          <StatTile
            label="Aprobados"
            value={String(todayStats.approved)}
            accentColor={colors.olive}
          />
          <StatTile
            label="Rechazados"
            value={String(todayStats.rejected)}
            accentColor={colors.terracotta}
          />
        </View>
      </View>

      <View style={styles.linksRow}>
        <Link href="/history" asChild>
          <Pressable style={styles.linkCard}>
            <Text style={styles.linkCardTitle}>Historial</Text>
            <Text style={styles.linkCardHint}>Ver inspecciones pasadas</Text>
          </Pressable>
        </Link>
        <Link href="/analytics" asChild>
          <Pressable style={styles.linkCard}>
            <Text style={styles.linkCardTitle}>Analítica</Text>
            <Text style={styles.linkCardHint}>Tasas de aprobación</Text>
          </Pressable>
        </Link>
      </View>

      {SHOW_DEBUG ? <BackendConnectionDev /> : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: spacing.lg,
    gap: spacing.lg,
    backgroundColor: colors.background,
  },
  header: {
    gap: 4,
    marginTop: spacing.sm,
  },
  title: {
    fontSize: 30,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  subtitle: {
    fontSize: 15,
    color: colors.textSecondary,
  },
  primaryCard: {
    backgroundColor: colors.graphite,
    borderRadius: radius.lg,
    padding: spacing.lg,
    gap: 4,
  },
  primaryCardLabel: {
    color: colors.textInverse,
    fontSize: 20,
    fontWeight: '700',
  },
  primaryCardHint: {
    color: colors.background,
    opacity: 0.75,
    fontSize: 13,
  },
  section: {
    gap: spacing.sm,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  linksRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  linkCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: 4,
  },
  linkCardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  linkCardHint: {
    fontSize: 12,
    color: colors.textSecondary,
  },
});
