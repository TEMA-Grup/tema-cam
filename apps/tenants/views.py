from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import SelectTenantForm
from .utils import get_tenant_model

@login_required
def select_tenant(request):
    # Kullanıcının sahip olduğu tenantlar (mevcut M2M: user.companies)
    # İleride 'tenants' üyeliği ile değiştirilebilir.
    Model = get_tenant_model()
    user_qs = request.user.companies.all().only("id", "name", "slug")  # mevcut yapına göre
    choices = [(t.slug, getattr(t, "name", str(t))) for t in user_qs]

    if not choices:
        return render(request, "tenants/no_tenant.html", status=403)

    if request.method == "POST":
        form = SelectTenantForm(request.POST, choices=choices)
        if form.is_valid():
            slug = form.cleaned_data["tenant"]
            request.session["active_company_slug"] = slug  # mevcut isimle uyumlu
            return redirect(reverse("core:landing", kwargs={"company": slug}))
    else:
        initial = {}
        current = getattr(request.user, "active_company", None)  # mevcut alan
        if current and user_qs.filter(pk=current.pk).exists():
            initial = {"tenant": current.slug}
        form = SelectTenantForm(choices=choices, initial=initial)

    return render(request, "tenants/select_tenant.html", {"form": form})

@login_required
def switch_tenant(request):
    return redirect("tenants:select")
