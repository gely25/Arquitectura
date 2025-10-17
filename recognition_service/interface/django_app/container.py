"""Dependency wiring for the Django interface layer."""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings

from recognition_service.recognition.application.services import RecognitionService
from recognition_service.recognition.infrastructure.camera import CameraAdapter
from recognition_service.recognition.infrastructure.detector import YOLODetector
from recognition_service.recognition.infrastructure.storage import FileSystemStorageAdapter


@lru_cache(maxsize=1)
def build_recognition_service() -> RecognitionService:
    """Instantiate the recognition service with concrete adapters."""
    detector = YOLODetector(getattr(settings, "YOLO_MODEL_PATH", None))
    camera = CameraAdapter(detector=detector)
    storage = FileSystemStorageAdapter(settings.MEDIA_ROOT)
    return RecognitionService(camera_port=camera, detector_port=detector, storage_port=storage)
