# recognition_service/recognition_service/urls.py

from django.contrib import admin
from django.urls import path,include
from api.views import DetectView, objects_view, video_feed, live_view
from django.conf import settings
from django.conf.urls.static import static


from django.contrib import admin
from django.urls import path
from api.views import (
    DetectView,
    objects_view,
    video_feed,
    live_view,
    start_camera_view,
    stop_camera_view
)

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

    # Endpoints para activar/desactivar cámara
    path('api/start_camera/', start_camera_view, name='start_camera'),
    path('api/stop_camera/', stop_camera_view, name='stop_camera'),
]



# Esto permite servir media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)