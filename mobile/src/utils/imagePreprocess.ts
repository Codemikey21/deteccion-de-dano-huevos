import * as ImageManipulator from 'expo-image-manipulator';

import { MAX_UPLOAD_DIMENSION } from '../constants/detectionVisual';

export interface PreprocessResult {
  uri: string;
  width: number;
  height: number;
  preprocessMs: number;
  resized: boolean;
}

function getResizeAction(
  width: number,
  height: number,
): ImageManipulator.Action | null {
  const maxSide = Math.max(width, height);
  if (maxSide <= MAX_UPLOAD_DIMENSION) {
    return null;
  }

  if (width >= height) {
    return { resize: { width: MAX_UPLOAD_DIMENSION } };
  }

  return { resize: { height: MAX_UPLOAD_DIMENSION } };
}

export async function preprocessCapture(uri: string): Promise<PreprocessResult> {
  const start = Date.now();
  const probe = await ImageManipulator.manipulateAsync(uri, [], {});

  const resizeAction = getResizeAction(probe.width, probe.height);
  if (!resizeAction) {
    return {
      uri,
      width: probe.width,
      height: probe.height,
      preprocessMs: Date.now() - start,
      resized: false,
    };
  }

  const result = await ImageManipulator.manipulateAsync(
    uri,
    [resizeAction],
    {
      compress: 0.72,
      format: ImageManipulator.SaveFormat.JPEG,
    },
  );

  return {
    uri: result.uri,
    width: result.width,
    height: result.height,
    preprocessMs: Date.now() - start,
    resized: true,
  };
}
