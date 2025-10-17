from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing helper
    import numpy as np


def clamp(value: int, lower: int, upper: int) -> int:
    """Ensure a value is kept within a valid image boundary."""
    return max(lower, min(value, upper))


@dataclass(frozen=True)
class BoundingBox:
    """Coordinates describing a detection bounding box."""

    x1: int
    y1: int
    x2: int
    y2: int

    def clamp_to_frame(self, height: int, width: int) -> BoundingBox:
        """Return a new bounding box clamped to the provided frame size."""
        return BoundingBox(
            clamp(self.x1, 0, width),
            clamp(self.y1, 0, height),
            clamp(self.x2, 0, width),
            clamp(self.y2, 0, height),
        )


@dataclass(frozen=True)
class Detection:
    """Represents a single detection returned by a detection model."""

    label: str
    confidence: Optional[float]
    bbox: BoundingBox

    def as_dict(self, include_bbox: bool = True, include_confidence: bool = True) -> dict:
        payload: dict[str, object] = {"label": self.label}
        if include_confidence and self.confidence is not None:
            payload["confidence"] = self.confidence
        if include_bbox:
            payload["bbox"] = [self.bbox.x1, self.bbox.y1, self.bbox.x2, self.bbox.y2]
        return payload


@dataclass
class CameraState:
    """Stores the latest frame and detections produced by the camera feed."""

    frame: Optional["np.ndarray"]
    detections: list[Detection]
