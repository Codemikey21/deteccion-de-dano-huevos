import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../constants/theme';

interface StatTileProps {
  label: string;
  value: string;
  accentColor?: string;
}

export function StatTile({ label, value, accentColor = colors.graphite }: StatTileProps) {
  return (
    <View style={styles.tile}>
      <Text style={[styles.value, { color: accentColor }]}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tile: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    alignItems: 'center',
    gap: 4,
  },
  value: {
    fontSize: 22,
    fontWeight: '700',
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textSecondary,
    textAlign: 'center',
  },
});
