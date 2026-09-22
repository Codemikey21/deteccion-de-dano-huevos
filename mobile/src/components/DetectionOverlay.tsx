import { StyleSheet, Text, View } from 'react-native';

import type { Detection } from '../types/prediction';
import { mapDetectionsToPreview, type PreviewSize } from '../utils/bbox';

interface DetectionOverlayProps {
  detections: Detection[];
  imageWidth: number;
  imageHeight: number;
  preview: PreviewSize;
}

function boxColor(className: string): string {
  return className === 'crack' ? '#ef4444' : '#22c55e';
}

export function DetectionOverlay({
  detections,
  imageWidth,
  imageHeight,
  preview,
}: DetectionOverlayProps) {
  if (preview.width <= 0 || preview.height <= 0 || detections.length === 0) {
    return null;
  }

  const mapped = mapDetectionsToPreview(
    detections,
    imageWidth,
    imageHeight,
    preview,
    'cover',
  );

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {mapped.map((detection, index) => {
        const { preview_bbox: box } = detection;
        if (box.width <= 0 || box.height <= 0) {
          return null;
        }

        return (
          <View
            key={`${detection.class_id}-${index}-${box.x1}-${box.y1}`}
            style={[
              styles.box,
              {
                left: box.x1,
                top: box.y1,
                width: box.width,
                height: box.height,
                borderColor: boxColor(detection.class_name),
              },
            ]}
          >
            <Text style={[styles.label, { backgroundColor: boxColor(detection.class_name) }]}>
              {detection.class_name} {detection.confidence.toFixed(2)}
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
