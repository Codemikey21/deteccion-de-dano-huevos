import { useEffect, useMemo, useState } from 'react';

import { computeInspectionStats, getInspections, subscribeToInspections } from '../services/inspectionStorage';
import type { Inspection } from '../types/inspection';

export interface UseInspectionsResult {
  inspections: Inspection[];
  loading: boolean;
  stats: ReturnType<typeof computeInspectionStats>;
}

export function useInspections(): UseInspectionsResult {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    getInspections().then((list) => {
      if (mounted) {
        setInspections(list);
        setLoading(false);
      }
    });

    const unsubscribe = subscribeToInspections((list) => {
      if (mounted) {
        setInspections(list);
      }
    });

    return () => {
      mounted = false;
      unsubscribe();
    };
  }, []);

  const stats = useMemo(() => computeInspectionStats(inspections), [inspections]);

  return { inspections, loading, stats };
}
