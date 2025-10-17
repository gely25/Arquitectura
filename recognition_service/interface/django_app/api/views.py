from __future__ import annotations

from typing import Iterable

from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from recognition_service.interface.django_app.container import build_recognition_service


def _frame_response(stream: Iterable[bytes]) -> Iterable[bytes]:
    for frame_bytes in stream:
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


_service = build_recognition_service()


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
