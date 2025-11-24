import io
from typing import Dict, Any

import cv2
import numpy as np


def annotate(frame_bytes: bytes, detections: Dict[str, Any]) -> bytes:
    buf = np.frombuffer(frame_bytes, dtype=np.uint8)
    image = cv2.imdecode(buf, cv2.IMREAD_COLOR)

    boxes = detections.get("boxes", [])
    labels = detections.get("labels", [])
    scores = detections.get("scores", [])

    for box, label, score in zip(boxes, labels, scores):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = f"{label}:{score:.2f}"
        cv2.putText(image, text, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError("Failed to encode annotated frame")
    return buffer.tobytes()
