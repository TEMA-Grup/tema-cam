from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from companies.models import Company
from django.http import HttpResponseForbidden

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        try:
            select_company_url = reverse("select_company")
        except Exception:
            select_company_url = "/select-company/"

        exempt_prefixes = (
            "/admin/",
            "/accounts/",
            getattr(settings, "STATIC_URL", "/static/"),
            getattr(settings, "MEDIA/URL", "/media/"),
        )

        if path == select_company_url or any(path.startswith(p) for p in exempt_prefixes):
            request.tenant = None
            return self.get_response(request)
        
        parts = path.lstrip("/").split("/", 1)
        slug = parts[0] if parts else ""

        tenant = Company.objects.filter(slug=slug).first()
        if tenant:
            request.tenant = tenant
            if request.user.is_authenticated and not request.user.companies.filter(pk=tenant.pk).exists():
                return HttpResponseForbidden("Bu şirkete erişiminiz yok.")
            return self.get_response(request)
        
        if request.user.is_authenticated:
            return redirect(select_company_url)
        
        return self.get_response(request)