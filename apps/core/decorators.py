from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def tenant_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return redirect("tenants:select")
        if request.user.is_authenticated and not request.user.companies.filter(pk=tenant.pk).exists():
            return HttpResponseForbidden("Bu şirkete erişiminiz yok.")
        return view_func(request, *args, **kwargs)
    return _wrapped
