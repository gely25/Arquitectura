from django.db import models

# api/models.py
from django.db import models

class MediaFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
