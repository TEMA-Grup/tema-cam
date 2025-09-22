from django.http import HttpResponseForbidden
from django.shortcuts import redirect

class TenantRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return redirect("select_company")
        if request.user.is_authenticated and not request.user.companies.filter(pk=tenant.pk).exists():
            return HttpResponseForbidden("Bu şirkete erişiminiz yok.")
        return super().dispatch(request, *args, **kwargs)