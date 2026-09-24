import { Text, type ColorValue } from 'react-native';

const GLYPHS = {
  home: '⌂',
  scan: '◎',
  history: '☰',
  analytics: '▦',
} as const;

interface TabIconProps {
  name: keyof typeof GLYPHS;
  color: ColorValue;
}

/** Glifos tipográficos en vez de una librería de iconos — mantiene el bundle liviano. */
export function TabIcon({ name, color }: TabIconProps) {
  return <Text style={{ fontSize: 20, color }}>{GLYPHS[name]}</Text>;
}
