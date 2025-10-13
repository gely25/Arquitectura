from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.shortcuts import redirect

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),

    # Página principal / home
    path('', TemplateView.as_view(template_name='recognition/live.html'), name='home'),

    # Página del portal de reconocimiento
    path('live/', TemplateView.as_view(template_name='recognition/live.html'), name='live'),

    # Redirecciones hacia el microservicio de reconocimiento
    path('objects/', lambda r: redirect('http://127.0.0.1:8001/api/labels/'), name='objects_view'),
    path('detect/', lambda r: redirect('http://127.0.0.1:8001/api/detect/'), name='detect'),

    # Streaming de video del microservicio de reconocimiento
    path('live/video_feed/', lambda r: redirect('http://127.0.0.1:8001/video_feed/'), name='video_feed'),

    # Redirecciones hacia el microservicio de flashcards
    path('flashcards/add/', lambda r: redirect('http://127.0.0.1:8002/api/flashcards/add/'), name='add_flashcard'),
    path('flashcards/list/', lambda r: redirect('http://127.0.0.1:8002/api/flashcards/list/'), name='flashcards_list'),
    path('flashcards/review/', lambda r: redirect('http://127.0.0.1:8002/api/flashcards/review/'), name='review_flashcards'),
]
