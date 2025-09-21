# recognition_service/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import os
import cv2
import numpy as np
from ultralytics import YOLO

# ==================================
# Cargar modelo YOLOv8 (nano)
# ==================================
model = YOLO("yolov8n.pt")

# Variables para streaming en tiempo real
last_labels = []
last_boxes = []
last_frame = None

# ==================================
# Streaming de cámara (opcional)
# ==================================
def gen_frames():
    global last_labels, last_boxes, last_frame
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break

        results = model(frame)

        labels = []
        boxes = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                labels.append(label)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((label, x1, y1, x2, y2))

        last_labels = list(set(labels))
        last_boxes = boxes
        last_frame = frame.copy()

        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode(".jpg", annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

def video_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )

def live_view(request):
    """Página HTML con el streaming de cámara"""
    return render(request, "recognition/live.html")

# ==================================
# Endpoint principal: detectar objetos
# ==================================
class DetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        # Leer imagen con OpenCV
        np_img = np.frombuffer(image_file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Guardar imagen en MEDIA_ROOT
        save_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
        with open(save_path, 'wb') as f:
            f.write(np_img)

        # Detectar objetos
        results = model(frame)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })

        return Response({"detections": detections})

# ==================================
# Endpoint para devolver últimas detecciones sin imagen
# ==================================
def objects_view(request):
    global last_labels
    return JsonResponse({"labels": last_labels})
