from __future__ import annotations

from typing import Iterable, Protocol, TYPE_CHECKING

from .entities import CameraState, Detection

if TYPE_CHECKING:  # pragma: no cover - typing helper
    import numpy as np

class CameraPort(Protocol):
    """Port that defines the behaviour required from a camera gateway."""

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def is_active(self) -> bool:
        ...

    def latest_state(self) -> CameraState:
        ...

    def frame_stream(self) -> Iterable[bytes]:
        ...


class DetectionModelPort(Protocol):
    """Port describing an object detection model."""

    def predict(self, frame: "np.ndarray", include_crops: bool = False) -> list[Detection]:
        ...


class StoragePort(Protocol):
    """Port that persists binary content for later access."""

    def save(self, filename: str, content: bytes) -> str:
        ...
