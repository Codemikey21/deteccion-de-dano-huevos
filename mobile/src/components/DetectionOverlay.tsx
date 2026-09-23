import { StyleSheet, Text, View } from 'react-native';

import type { VisualBox } from '../hooks/useEggVision';
import type { PreviewSize } from '../utils/bboxTransform';

interface DetectionOverlayProps {
  visualBoxes: VisualBox[];
  preview: PreviewSize;
}

export function DetectionOverlay({ visualBoxes, preview }: DetectionOverlayProps) {
  if (preview.width <= 0 || preview.height <= 0 || visualBoxes.length === 0) {
    return null;
  }

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {visualBoxes.map((box, index) => {
        const previewBox = box.previewBbox;

        return (
          <View
            key={`${box.className}-${box.confidence}-${index}`}
            style={[
              styles.box,
              {
                left: previewBox.x1,
                top: previewBox.y1,
                width: previewBox.width,
                height: previewBox.height,
                borderColor: box.color,
              },
            ]}
          >
            <Text style={[styles.label, { backgroundColor: box.color }]}>
              {box.className} {box.confidence.toFixed(2)}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    position: 'absolute',
    borderWidth: 2,
  },
  label: {
    position: 'absolute',
    top: -18,
    left: -2,
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
    paddingHorizontal: 4,
    paddingVertical: 1,
    overflow: 'hidden',
  },
});
