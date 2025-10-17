from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from api.views import (
    DetectView,
    live_view,
    objects_view,
    start_camera_view,
    stop_camera_view,
    video_feed,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/detect/", DetectView.as_view(), name="detect"),
    path("api/labels/", objects_view, name="labels"),
    path("video_feed/", video_feed, name="video_feed"),
    path("live/", live_view, name="live_view"),
    path("api/start_camera/", start_camera_view, name="start_camera"),
    path("api/stop_camera/", stop_camera_view, name="stop_camera"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
