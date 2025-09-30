from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # DİKKAT: import yok, string referans var
    companies = models.ManyToManyField(
        'companies.Company', blank=True, related_name='users'
    )
    active_company = models.ForeignKey(
        'companies.Company', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
