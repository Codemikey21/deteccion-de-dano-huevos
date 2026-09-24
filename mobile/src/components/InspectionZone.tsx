import { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import Animated, {
  cancelAnimation,
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';

import { colors } from '../constants/theme';
import type { DisplayStatus } from '../types/prediction';

interface InspectionZoneProps {
  status: DisplayStatus;
}

function zoneColor(status: DisplayStatus): string {
  switch (status) {
    case 'approved':
      return colors.olive;
    case 'rejected':
      return colors.terracotta;
    case 'review':
      return colors.amber;
    default:
      return colors.background;
  }
}

/**
 * Marco fijo de encuadre — reemplaza los bounding boxes crudos del modelo,
 * que están mal localizados y no deben mostrarse en la versión de presentación.
 */
export function InspectionZone({ status }: InspectionZoneProps) {
  const pulse = useSharedValue(0);

  useEffect(() => {
    if (status === 'detecting') {
      pulse.value = withRepeat(
        withTiming(1, { duration: 1300, easing: Easing.inOut(Easing.ease) }),
        -1,
        true,
      );
    } else {
      cancelAnimation(pulse);
      pulse.value = withTiming(0, { duration: 250 });
    }

    return () => cancelAnimation(pulse);
  }, [status, pulse]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: 0.5 + pulse.value * 0.35,
    transform: [{ scale: 1 + pulse.value * 0.02 }],
  }));

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <View style={styles.center}>
        <Animated.View
          style={[
            styles.zone,
            { borderColor: zoneColor(status) },
            status === 'detecting' ? styles.zoneDashed : null,
            animatedStyle,
          ]}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  zone: {
    width: '66%',
    aspectRatio: 0.76,
    borderRadius: 999,
    borderWidth: 3,
  },
  zoneDashed: {
    borderStyle: 'dashed',
  },
});
