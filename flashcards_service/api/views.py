from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Flashcard
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Flashcard

@csrf_exempt
def add_flashcard(request):
    if request.method == "POST":
        data = json.loads(request.body)
        palabra = data.get("palabra") 
        traduccion = data.get("traduccion") 

        if not palabra or not traduccion:
            return JsonResponse({"error": "Falta palabra o traduccion"}, status=400)

        flashcard = Flashcard.objects.create(
            palabra=palabra,
            traduccion=traduccion
        )
        return JsonResponse({"id": flashcard.id, "palabra": flashcard.palabra, "traduccion": flashcard.traduccion})


def flashcards_list(request):
    flashcards = Flashcard.objects.all()
    data = [{"id": f.id, "palabra": f.palabra, "traduccion": f.traduccion} for f in flashcards]
    return JsonResponse(data, safe=False)
