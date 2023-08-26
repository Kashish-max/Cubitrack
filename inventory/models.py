from django.db import models
from django.contrib.auth import get_user_model

from backend.utils.models import BaseModel

User = get_user_model()


class Box(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    length = models.IntegerField()
    breadth = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        ordering = ("-created_on",)
