from django.urls import path
from .views import landing

app_name="core"

urlpatterns=[
    path("", landing, name="landing"),
]