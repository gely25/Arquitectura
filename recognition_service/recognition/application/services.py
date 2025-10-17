from __future__ import annotations

import base64
from typing import Iterable

import cv2
import numpy as np

from ..domain.entities import CameraState, Detection
from ..domain.ports import CameraPort, DetectionModelPort, StoragePort


class RecognitionService:
    """Application service orchestrating the object recognition workflow."""

    def __init__(
        self,
        camera_port: CameraPort,
        detector_port: DetectionModelPort,
        storage_port: StoragePort,
    ) -> None:
        self._camera = camera_port
        self._detector = detector_port
        self._storage = storage_port

    # ---------------------------------------------------------------------
    # Camera controls
    # ---------------------------------------------------------------------
    def start_camera(self) -> None:
        self._camera.start()

    def stop_camera(self) -> None:
        self._camera.stop()

    def is_camera_active(self) -> bool:
        return self._camera.is_active()

    # ------------------------------------------------------------------
    # Streaming helpers
    # ------------------------------------------------------------------
    def frame_stream(self) -> Iterable[bytes]:
        return self._camera.frame_stream()

    def latest_state(self) -> CameraState:
        return self._camera.latest_state()

    def latest_detected_objects(self) -> list[dict]:
        state = self.latest_state()
        if state.frame is None:
            return []

        height, width = state.frame.shape[:2]
        seen_labels: set[str] = set()
        response: list[dict] = []

        for detection in state.detections:
            if detection.label in seen_labels:
                continue
            seen_labels.add(detection.label)

            bbox = detection.bbox.clamp_to_frame(height, width)
            crop = state.frame[bbox.y1 : bbox.y2, bbox.x1 : bbox.x2]
            if crop.size == 0:
                continue
            _, buffer = cv2.imencode(".jpg", crop)
            base64_image = base64.b64encode(buffer.tobytes()).decode("utf-8")

            payload = detection.as_dict()
            payload["image"] = f"data:image/jpeg;base64,{base64_image}"
            response.append(payload)

        return response

    # ------------------------------------------------------------------
    # Image detection workflow
    # ------------------------------------------------------------------
    def detect_from_image(self, filename: str, content: bytes) -> list[dict]:
        frame = self._decode_image(content)
        self._storage.save(filename, content)
        detections = self._detector.predict(frame, include_crops=True)
        return [self._serialize_detection(detection, frame) for detection in detections]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _decode_image(self, content: bytes) -> np.ndarray:
        np_img = np.frombuffer(content, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("The provided bytes could not be decoded as an image")
        return frame

    def _serialize_detection(self, detection: Detection, frame: np.ndarray) -> dict:
        height, width = frame.shape[:2]
        bbox = detection.bbox.clamp_to_frame(height, width)
        crop = frame[bbox.y1 : bbox.y2, bbox.x1 : bbox.x2]
        _, buffer = cv2.imencode(".jpg", crop)
        payload = detection.as_dict(include_confidence=True)
        payload["image"] = f"data:image/jpeg;base64,{base64.b64encode(buffer.tobytes()).decode('utf-8')}"
        return payload
