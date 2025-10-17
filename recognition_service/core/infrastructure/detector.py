from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from ultralytics import YOLO

from ..domain.entities import BoundingBox, Detection
from ..domain.ports import DetectionModelPort


class YOLODetector(DetectionModelPort):
    """Adapter that wraps a YOLO model to fulfil the detection port."""

    def __init__(self, model_path: Optional[str | Path] = None) -> None:
        self._model = YOLO(model_path or "yolov8n.pt")

    def predict(self, frame: np.ndarray, include_crops: bool = False) -> list[Detection]:
        results = self._model(frame)
        detections: list[Detection] = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = self._model.names[cls_id]
                confidence = float(box.conf[0]) if box.conf is not None else None
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(
                    Detection(
                        label=label,
                        confidence=confidence,
                        bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                    )
                )

        return detections
