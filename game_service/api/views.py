from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

@api_view(['POST'])
def submit_gesture(request):
    """
    Recibe un archivo 'image' y un campo 'target' con la etiqueta esperada.
    Envía la imagen a recognition-service y valida si la detección contiene el target.
    """
    target = request.data.get('target')
    image = request.FILES.get('image')
    if not image or not target:
        return Response({"error": "image and target required"}, status=400)

    # forward file to recognition-service
    files = {'image': (image.name, image.read(), image.content_type)}
    try:
        r = requests.post('http://127.0.0.1:8002/api/detect/', files=files, timeout=5)
        r.raise_for_status()
    except Exception as e:
        return Response({"error": "recognition service error", "details": str(e)}, status=500)

    detections = r.json().get('detections', [])
    # simple check: any label == target
    found = any(d.get('label') == target for d in detections)
    return Response({"target": target, "found": found, "detections": detections})
