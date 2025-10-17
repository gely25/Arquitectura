from __future__ import annotations

import threading
import time
from typing import Iterable

import cv2

from ..domain.entities import CameraState
from ..domain.ports import CameraPort, DetectionModelPort


class CameraAdapter(CameraPort):
    """Camera adapter that continuously captures frames and detections."""

    def __init__(
        self,
        detector: DetectionModelPort,
        camera_index: int = 0,
        sleep_interval: float = 0.01,
    ) -> None:
        self._detector = detector
        self._camera_index = camera_index
        self._sleep_interval = sleep_interval

        self._lock = threading.Lock()
        self._state = CameraState(frame=None, detections=[])

        self._thread: threading.Thread | None = None
        self._active = False

    def start(self) -> None:
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._active = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def is_active(self) -> bool:
        return self._active

    def latest_state(self) -> CameraState:
        with self._lock:
            frame_copy = None if self._state.frame is None else self._state.frame.copy()
            detections_copy = list(self._state.detections)
        return CameraState(frame=frame_copy, detections=detections_copy)

    def frame_stream(self) -> Iterable[bytes]:
        while self._active:
            state = self.latest_state()
            if state.frame is None:
                time.sleep(0.05)
                continue
            success, buffer = cv2.imencode(".jpg", state.frame)
            if not success:
                continue
            yield buffer.tobytes()

    # ------------------------------------------------------------------
    # Internal capture loop
    # ------------------------------------------------------------------
    def _capture_loop(self) -> None:
        cap = cv2.VideoCapture(self._camera_index)
        try:
            while self._active:
                success, frame = cap.read()
                if not success:
                    time.sleep(0.1)
                    continue

                detections = self._detector.predict(frame)
                with self._lock:
                    self._state = CameraState(frame=frame.copy(), detections=detections)

                time.sleep(self._sleep_interval)
        finally:
            cap.release()
