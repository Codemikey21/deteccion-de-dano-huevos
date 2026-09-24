import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../constants/theme';

interface ApprovalBarProps {
  approvedPct: number;
  rejectedPct: number;
}

/** Barra horizontal segmentada — evita agregar una librería de gráficos solo para esto. */
export function ApprovalBar({ approvedPct, rejectedPct }: ApprovalBarProps) {
  const hasData = approvedPct + rejectedPct > 0;

  return (
    <View>
      <View style={styles.track}>
        {hasData ? (
          <>
            <View style={[styles.segment, { flex: approvedPct, backgroundColor: colors.olive }]} />
            <View
              style={[styles.segment, { flex: rejectedPct, backgroundColor: colors.terracotta }]}
            />
          </>
        ) : (
          <View style={[styles.segment, { flex: 1, backgroundColor: colors.surfaceMuted }]} />
        )}
      </View>
      <View style={styles.legendRow}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: colors.olive }]} />
          <Text style={styles.legendText}>Aprobados {approvedPct.toFixed(0)}%</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: colors.terracotta }]} />
          <Text style={styles.legendText}>Rechazados {rejectedPct.toFixed(0)}%</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    flexDirection: 'row',
    height: 14,
    borderRadius: radius.pill,
    overflow: 'hidden',
    backgroundColor: colors.surfaceMuted,
  },
  segment: {
    height: '100%',
  },
  legendRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textSecondary,
  },
});
