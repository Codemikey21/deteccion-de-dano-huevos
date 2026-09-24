import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { ApprovalBar } from '../src/components/ApprovalBar';
import { EmptyState } from '../src/components/EmptyState';
import { StatTile } from '../src/components/StatTile';
import { colors, radius, spacing } from '../src/constants/theme';
import { useInspections } from '../src/hooks/useInspections';

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString('es', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function AnalyticsScreen() {
  const { stats, loading } = useInspections();

  if (!loading && stats.total === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Analítica</Text>
        <EmptyState
          title="Aún no hay datos"
          subtitle="Realiza inspecciones en Scan para ver estadísticas"
        />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Analítica</Text>

      <View style={styles.statsRow}>
        <StatTile label="Total" value={String(stats.total)} />
        <StatTile label="Aprobados" value={String(stats.approved)} accentColor={colors.olive} />
        <StatTile
          label="Rechazados"
          value={String(stats.rejected)}
          accentColor={colors.terracotta}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Distribución de resultados</Text>
        <ApprovalBar approvedPct={stats.approvedPct} rejectedPct={stats.rejectedPct} />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Última inspección</Text>
        {stats.lastInspection ? (
          <Text style={styles.cardValue}>
            {stats.lastInspection.status === 'approved' ? 'Aprobado' : 'Rechazado'} ·{' '}
            {formatTimestamp(stats.lastInspection.timestamp)}
          </Text>
        ) : (
          <Text style={styles.cardMuted}>Sin registros</Text>
        )}
      </View>

      {stats.avgInferenceMs !== null ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Tiempo promedio de análisis</Text>
          <Text style={styles.cardValue}>{Math.round(stats.avgInferenceMs)} ms</Text>
        </View>
      ) : null}
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
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  cardTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  cardValue: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  cardMuted: {
    fontSize: 14,
    color: colors.textSecondary,
  },
});
