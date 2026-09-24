import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../constants/theme';
import type { Inspection } from '../types/inspection';

interface InspectionListItemProps {
  inspection: Inspection;
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  const datePart = date.toLocaleDateString('es', { day: '2-digit', month: 'short' });
  const timePart = date.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' });
  return `${datePart} · ${timePart}`;
}

export function InspectionListItem({ inspection }: InspectionListItemProps) {
  const isApproved = inspection.status === 'approved';
  const accent = isApproved ? colors.olive : colors.terracotta;
  const bg = isApproved ? colors.oliveSoft : colors.terracottaSoft;

  return (
    <View style={styles.row}>
      <View style={[styles.icon, { backgroundColor: bg }]}>
        <View style={[styles.dot, { backgroundColor: accent }]} />
      </View>

      <View style={styles.info}>
        <Text style={styles.status}>
          {isApproved ? 'Huevo aprobado' : 'Huevo rechazado'}
        </Text>
        <Text style={styles.meta}>{formatTimestamp(inspection.timestamp)}</Text>
      </View>

      <View style={styles.right}>
        <Text style={[styles.crack, { color: accent }]}>
          {inspection.crackDetected ? 'Grieta detectada' : 'Sin grietas'}
        </Text>
        {typeof inspection.inferenceMs === 'number' ? (
          <Text style={styles.timing}>{inspection.inferenceMs} ms</Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  icon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  info: {
    flex: 1,
    gap: 2,
  },
  status: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  meta: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  right: {
    alignItems: 'flex-end',
    gap: 2,
  },
  crack: {
    fontSize: 12,
    fontWeight: '700',
  },
  timing: {
    fontSize: 11,
    color: colors.textSecondary,
  },
});
