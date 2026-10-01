# Demo regression scenes

Camera-area crops of nine screenshots supplied by the user during the demo.
No app chrome or user identifiers are included. These are preview screenshots,
not the exact frames submitted to the API; they validate this failure case,
not general accuracy or camera/network latency. Keep them out of training.

Expected visible objects: 4, 1, 1, 2, 2, 2, 4, 4, 4.
Scenes 1–3 and 7–9 include one egg with a dark scribble. Scenes 4–6 include
one visibly chipped egg; classifying this break uses full-frame YOLO evidence,
not the dark-mark heuristic. No temporal smoothing or repeated detections
are used to manufacture these counts.
