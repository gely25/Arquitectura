from __future__ import annotations

from typing import Iterable

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from recognition_service.core.application.services import RecognitionService
from recognition_service.core.infrastructure.camera import CameraAdapter
from recognition_service.core.infrastructure.detector import YOLODetector
from recognition_service.core.infrastructure.storage import FileSystemStorageAdapter


def _frame_response(stream: Iterable[bytes]) -> Iterable[bytes]:
    for frame_bytes in stream:
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


def _build_service() -> RecognitionService:
    detector = YOLODetector(getattr(settings, "YOLO_MODEL_PATH", None))
    camera = CameraAdapter(detector=detector)
    storage = FileSystemStorageAdapter(settings.MEDIA_ROOT)
    return RecognitionService(camera_port=camera, detector_port=detector, storage_port=storage)


_service = _build_service()


class DetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):  # noqa: D401 - REST framework signature
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        detections = _service.detect_from_image(image_file.name, image_file.read())
        return Response({"detections": detections})


def live_view(request):
    return render(request, "recognition/live.html")


def video_feed(request):
    _service.start_camera()
    return StreamingHttpResponse(
        _frame_response(_service.frame_stream()),
        content_type="multipart/x-mixed-replace; boundary=frame",
    )


@csrf_exempt
def start_camera_view(request):
    _service.start_camera()
    return JsonResponse({"status": "camera-started"})


@csrf_exempt
def stop_camera_view(request):
    _service.stop_camera()
    return JsonResponse({"status": "camera-stopped"})


def objects_view(request):
    return JsonResponse({"labels": _service.latest_detected_objects()})
