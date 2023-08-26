import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(db_index=True, default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

