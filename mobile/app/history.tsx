import { useMemo, useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';

import { EmptyState } from '../src/components/EmptyState';
import { FilterChips } from '../src/components/FilterChips';
import { InspectionListItem } from '../src/components/InspectionListItem';
import { colors, spacing } from '../src/constants/theme';
import { useInspections } from '../src/hooks/useInspections';
import type { Inspection } from '../src/types/inspection';

type FilterValue = 'all' | 'approved' | 'rejected';

const FILTER_OPTIONS: { value: FilterValue; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'approved', label: 'Aprobados' },
  { value: 'rejected', label: 'Rechazados' },
];

export default function HistoryScreen() {
  const { inspections, loading } = useInspections();
  const [filter, setFilter] = useState<FilterValue>('all');

  const filtered = useMemo(() => {
    if (filter === 'all') {
      return inspections;
    }
    return inspections.filter((item) => item.status === filter);
  }, [inspections, filter]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Historial</Text>
        <FilterChips options={FILTER_OPTIONS} value={filter} onChange={setFilter} />
      </View>

      <FlatList<Inspection>
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <InspectionListItem inspection={item} />}
        contentContainerStyle={styles.listContent}
        ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
        ListEmptyComponent={
          !loading ? (
            <EmptyState
              title="Aún no hay inspecciones"
              subtitle="Los resultados de Scan aparecerán aquí"
            />
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.lg,
    gap: spacing.md,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
    flexGrow: 1,
  },
});
