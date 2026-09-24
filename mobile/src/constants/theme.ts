/** Paleta y tokens visuales — línea industrial editorial (ivory / graphite / olive / amber / terracotta). */
export const colors = {
  background: '#F6F1E6',
  surface: '#FFFFFF',
  surfaceMuted: '#EEE7D6',
  border: '#E0D6C0',

  graphite: '#26241F',
  graphiteSoft: '#5B5648',
  textPrimary: '#26241F',
  textSecondary: '#726C5A',
  textInverse: '#F6F1E6',

  olive: '#67753F',
  oliveStrong: '#4C5730',
  oliveSoft: '#E1E7CD',

  amber: '#BD8228',
  amberStrong: '#8F621D',
  amberSoft: '#F1E1BA',

  terracotta: '#B0502E',
  terracottaStrong: '#833A21',
  terracottaSoft: '#F1DBCE',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

export const radius = {
  sm: 10,
  md: 16,
  lg: 24,
  pill: 999,
} as const;

export const typography = {
  h1: { fontSize: 28, fontWeight: '700' as const, color: colors.textPrimary },
  h2: { fontSize: 20, fontWeight: '700' as const, color: colors.textPrimary },
  body: { fontSize: 15, fontWeight: '400' as const, color: colors.textPrimary },
  caption: { fontSize: 13, fontWeight: '500' as const, color: colors.textSecondary },
  label: { fontSize: 12, fontWeight: '600' as const, color: colors.textSecondary },
};
