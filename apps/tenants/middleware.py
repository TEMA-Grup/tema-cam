from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden
from .utils import get_tenant_by_slug

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        try:
            select_url = reverse("tenants:select")
            switch_url = reverse("tenants:switch")
        except Exception:
            select_url = "/"
            switch_url = "/switch-tenant/"

        exempt_prefixes = (
            "/admin/",
            "/accounts/",
            getattr(settings, "STATIC_URL", "/static/"),
            getattr(settings, "MEDIA_URL", "/media/"),
            select_url, switch_url,
        )
        if path in (select_url, switch_url) or any(path.startswith(p) for p in exempt_prefixes):
            request.tenant = None
            return self.get_response(request)

        # /<slug>/... biçimi
        parts = path.lstrip("/").split("/", 1)
        slug = parts[0] if parts else ""
        tenant = get_tenant_by_slug(slug) if slug else None

        if tenant:
            request.tenant = tenant
            # Yetki: kullanıcı bu tenant'a bağlı mı?
            if request.user.is_authenticated and not request.user.companies.filter(pk=tenant.pk).exists():
                return HttpResponseForbidden("Bu tenant'a erişiminiz yok.")
            return self.get_response(request)

        # Tenant yoksa, girişli ise seçim sayfası
        if request.user.is_authenticated:
            return redirect(select_url)

        return self.get_response(request)
