from django.urls import path
from .views import select_tenant, switch_tenant

app_name = "tenants"
urlpatterns = [
    path("", select_tenant, name="select"),
    path("select-tenant/", select_tenant, name="select_alt"),
    path("switch-tenant/", switch_tenant, name="switch"),
]
