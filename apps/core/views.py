from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from companies.models import Company
from .forms import SelectCompanyForm

@login_required
def select_company(request):
    qs = request.user.companies.all()
    if not qs.exists():
        return render(request, "core/no_company.html", status=403)
    
    if qs.count() == 1:
        slug = qs.first().slug
        request.session["active_company_slug"] = slug
        return redirect(reverse("core:landing", kwargs={"company": slug}))
    
    if request.method == "POST":
        form = SelectCompanyForm(request.POST, companies=qs)
        if form.is_valid():
            slug = form.cleaned_data["company"]
            if not qs.filter(slug=slug).exists():
                return render(request, "core/no_company.html", status=403)
            request.session["active_company_slug"] = slug
            return redirect(reverse("core:landing", kwargs={"company": slug}))
    else:
        form = SelectCompanyForm(companies=qs)
    return render(request, "core/select_company.html", {"form": form})

def landing(request, company):
    return render(request, "core/landing.html")