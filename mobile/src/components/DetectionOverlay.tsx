import { useMemo } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import type { Detection } from '../types/prediction';
import {
  clampMappedBBox,
  mapDetectionsToPreview,
  type PreviewSize,
} from '../utils/bbox';
import { filterVisualDetections } from '../utils/detectionFilter';

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
  const visibleDetections = useMemo(() => {
    if (preview.width <= 0 || preview.height <= 0) {
      return [];
    }

    const filtered = filterVisualDetections(detections, imageWidth, imageHeight);
    const mapped = mapDetectionsToPreview(
      filtered,
      imageWidth,
      imageHeight,
      preview,
      'cover',
    );

    return mapped
      .map((detection) => {
        const clamped = clampMappedBBox(detection.preview_bbox, preview);
        if (!clamped) {
          return null;
        }
        return { ...detection, preview_bbox: clamped };
      })
      .filter(
        (detection): detection is Detection & { preview_bbox: NonNullable<ReturnType<typeof clampMappedBBox>> } =>
          detection !== null,
      );
  }, [detections, imageHeight, imageWidth, preview]);

  if (visibleDetections.length === 0) {
    return null;
  }

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {visibleDetections.map((detection) => {
        const box = detection.preview_bbox;

        return (
          <View
            key={`${detection.class_name}-${detection.confidence}-${box.x1}-${box.y1}`}
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
