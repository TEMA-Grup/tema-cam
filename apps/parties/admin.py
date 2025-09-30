from django.contrib import admin
from .models import Party, Role, PartyRole, RelationshipType, Relationship, Capability, RoleCapability, PartyCapability

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("display_name", "type", "company", "email", "is_active")
    list_filter = ("type", "company", "is_active")
    search_fields = ("first_name", "last_name", "trade_name", "legal_name", "email", "tax_id")

admin.site.register(Role)
admin.site.register(PartyRole)
admin.site.register(RelationshipType)
admin.site.register(Relationship)
admin.site.register(Capability)
admin.site.register(RoleCapability)
admin.site.register(PartyCapability)
