from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from apps.companies.models import Company

def landing(request, company):
    return render(request, "core/landing.html", {"tenant": getattr(request, "tenant", None)})
