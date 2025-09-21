from django.contrib import admin
from django.urls import path
from api.views import submit_gesture

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/game/submit/', submit_gesture),
]
