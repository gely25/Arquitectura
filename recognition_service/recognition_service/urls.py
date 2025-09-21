# recognition_service/recognition_service/urls.py

from django.contrib import admin
from django.urls import path
from api.views import DetectView, objects_view, video_feed, live_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoint para detección de objetos (POST con imagen)
    path('api/detect/', DetectView.as_view(), name='detect'),

    # Endpoint para obtener últimas etiquetas detectadas (GET)
    path('api/labels/', objects_view, name='labels'),

    # Streaming de cámara en tiempo real (opcional)
    path('video_feed/', video_feed, name='video_feed'),

    # Página HTML con el streaming
    path('live/', live_view, name='live_view'),
]
