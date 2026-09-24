import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from '../constants/theme';
import type { DisplayStatus } from '../types/prediction';

interface StatusCardProps {
  status: DisplayStatus;
}

const STATUS_COPY: Record<DisplayStatus, { title: string; subtitle: string }> = {
  detecting: {
    title: 'Buscando huevo...',
    subtitle: 'Ubica un huevo dentro del área de inspección',
  },
  review: {
    title: 'Analizando...',
    subtitle: 'Estamos verificando el estado del huevo',
  },
  approved: {
    title: 'Huevo aprobado',
    subtitle: 'No se detectaron grietas relevantes',
  },
  rejected: {
    title: 'Huevo rechazado',
    subtitle: 'Se detectó una posible grieta',
  },
};

function statusPalette(status: DisplayStatus): { bg: string; fg: string; dot: string } {
  switch (status) {
    case 'approved':
      return { bg: colors.oliveSoft, fg: colors.oliveStrong, dot: colors.olive };
    case 'rejected':
      return { bg: colors.terracottaSoft, fg: colors.terracottaStrong, dot: colors.terracotta };
    case 'review':
      return { bg: colors.amberSoft, fg: colors.amberStrong, dot: colors.amber };
    default:
      return { bg: colors.surfaceMuted, fg: colors.graphiteSoft, dot: colors.graphiteSoft };
  }
}

export function StatusCard({ status }: StatusCardProps) {
  const copy = STATUS_COPY[status];
  const palette = statusPalette(status);

  return (
    <View style={[styles.card, { backgroundColor: palette.bg }]}>
      <View style={[styles.dot, { backgroundColor: palette.dot }]} />
      <View style={styles.textGroup}>
        <Text style={[styles.title, { color: palette.fg }]}>{copy.title}</Text>
        <Text style={[styles.subtitle, { color: palette.fg }]}>{copy.subtitle}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.md,
    padding: spacing.lg,
    borderRadius: radius.lg,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginTop: 6,
  },
  textGroup: {
    flex: 1,
    gap: 4,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 14,
    lineHeight: 20,
  },
});
