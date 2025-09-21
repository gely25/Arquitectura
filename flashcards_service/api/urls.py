from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_flashcard, name="add_flashcard"),
    path("list/", views.flashcards_list, name="flashcards_list"),
]
