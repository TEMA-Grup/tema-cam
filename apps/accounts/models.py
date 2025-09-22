from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import Company

class User(AbstractUser):
    companies = models.ManyToManyField(Company, blank=True)
    active_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    