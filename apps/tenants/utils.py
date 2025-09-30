from django.conf import settings
from django.apps import apps as django_apps

def get_tenant_model():
    """
    settings.TENANT_MODEL = "companies.Company" gibi.
    İleride "tenants.Tenant" yaparsın, bu kod değişmez.
    """
    app_label, model_name = settings.TENANT_MODEL.split(".")
    return django_apps.get_model(app_label, model_name)

def get_tenant_by_slug(slug: str):
    Model = get_tenant_model()
    return Model.objects.filter(slug=slug).first()
