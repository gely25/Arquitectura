import threading
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import os
import cv2
import numpy as np
from ultralytics import YOLO
import base64

# ==================================
# Cargar modelo YOLOv8
# ==================================
model = YOLO("yolov8n.pt")

# Variables globales
last_labels = []
last_boxes = []
last_frame = None
camera_thread = None
camera_active = False

# Lock para sincronizar acceso a frame y detecciones
frame_lock = threading.Lock()


# ==================================
# Función de captura de cámara en thread
# ==================================
def camera_loop():
    global last_labels, last_boxes, last_frame, camera_active
    cap = cv2.VideoCapture(0)
    while camera_active:
        success, frame = cap.read()
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

        # Guardar resultados con lock para evitar conflictos
        with frame_lock:
            last_labels = list(set(labels))
            last_boxes = boxes
            last_frame = frame.copy()

        time.sleep(0.01)  # pequeña pausa para no saturar CPU

    cap.release()


# ==================================
# Streaming de cámara
# ==================================
def gen_frames():
    global last_frame, camera_active
    while camera_active:
        if last_frame is not None:
            with frame_lock:
                annotated_frame = last_frame.copy()
                # opcional: dibujar cajas si quieres
                # for label, x1, y1, x2, y2 in last_boxes:
                #     cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0,255,0), 2)
            
            ret, buffer = cv2.imencode(".jpg", annotated_frame)
            frame_bytes = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        else:
            time.sleep(0.05)


def video_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


def live_view(request):
    return render(request, "recognition/live.html")


# ==================================
# Activar / Desactivar cámara
# ==================================
def start_camera():
    global camera_thread, camera_active
    if not camera_active:
        camera_active = True
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.start()


def stop_camera():
    global camera_active, camera_thread
    camera_active = False
    if camera_thread is not None:
        camera_thread.join()  # espera a que el thread termine
        camera_thread = None


# ==================================
# Endpoint para detener la cámara desde frontend
# ==================================
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stop_camera_view(request):
    stop_camera()
    return JsonResponse({"status": "Camera stopped"})


# ==================================
# Endpoint para devolver últimas detecciones
# ==================================
def objects_view(request):
    global last_labels, last_boxes, last_frame
    labels_with_images = []

    with frame_lock:
        if last_frame is not None and last_boxes:
            seen = set()
            for label, x1, y1, x2, y2 in last_boxes:
                if label in seen:
                    continue
                seen.add(label)
                obj_crop = last_frame[y1:y2, x1:x2]
                _, buffer = cv2.imencode(".jpg", obj_crop)
                img_bytes = buffer.tobytes()
                base64_image = f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                labels_with_images.append({"label": label, "image": base64_image})

    return JsonResponse({"labels": labels_with_images})


# ==================================
# DetectView para detección de imágenes enviadas (igual que antes)
# ==================================
class DetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        np_img = np.frombuffer(image_file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        save_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
        with open(save_path, 'wb') as f:
            f.write(np_img)

        results = model(frame)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                obj_crop = frame[y1:y2, x1:x2]
                _, buffer = cv2.imencode(".jpg", obj_crop)
                img_bytes = buffer.tobytes()
                base64_image = f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                    "image": base64_image
                })

        return Response({"detections": detections})








from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def start_camera_view(request):
    start_camera()
    return JsonResponse({"status": "Camera started"})






########## Unión de API

from googletrans import Translator

translator = Translator()

def send_to_flashcards(label):
    url = "http://localhost:8002/api/flashcards/add/"
    traduccion = translator.translate(label, src="en", dest="es").text
    data = {
        "palabra": label,
        "traduccion": traduccion
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
