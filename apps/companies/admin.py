from django.contrib import admin
from apps.companies.models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
