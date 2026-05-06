from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Type(models.TextChoices):
        STORE = "store", "Loja verificada"
        FLYER = "flyer", "Folheto extraído"

    supabase_id = models.CharField(max_length=36, unique=True, db_index=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.STORE)
