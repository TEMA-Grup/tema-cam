from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models import Q

# ------- Sabitler
PARTY_TYPE = (
    ("person", "Kişi"),
    ("organization", "Kuruluş"),
)

SCOPE = (
    ("platform", "Platform"),
    ("tenant",   "Tenant"),
)

# ------- Çekirdek

class Party(models.Model):
    """
    Kişi/kuruluş ortak üst model.
    - scope: platform (company=None) veya tenant (company=Company)
    """
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE, null=True, blank=True,
        related_name='parties'
    )
    type = models.CharField(max_length=20, choices=PARTY_TYPE, default="person")

    # Kişi alanları
    first_name = models.CharField(max_length=120, blank=True)
    last_name  = models.CharField(max_length=120, blank=True)

    # Kuruluş alanları
    legal_name = models.CharField("Unvan", max_length=255, blank=True)
    trade_name = models.CharField("Ticari Ad", max_length=255, blank=True)

    # Ortak
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    tax_id = models.CharField("Vergi No/TCKN", max_length=64, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            # Aynı tenant/platform içinde aynı vergi no tekrar etmesin (boş hariç)
            models.UniqueConstraint(
                fields=["company", "tax_id"],
                condition=~Q(tax_id=""),
                name="uq_party_company_tax_id_not_blank",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "type"]),
            models.Index(fields=["company", "email"]),
        ]

    def __str__(self):
        return self.display_name

    @property
    def scope(self):
        return "platform" if self.company_id is None else "tenant"

    @property
    def display_name(self):
        if self.type == "organization":
            return self.trade_name or self.legal_name or "(Kuruluş)"
        name = f"{self.first_name} {self.last_name}".strip()
        return name or "(Kişi)"


class Role(models.Model):
    """
    platform_owner, tenant_owner, supplier, ...
    Global sözlük (scope farkı rollerde değil atamada belirir).
    """
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roller"

    def __str__(self):
        return self.name


class PartyRole(models.Model):
    """
    Bir Party'nin belirli bir tenant veya platform kapsamındaki rolü.
    - company=null => platform kapsamı (sistem çapı rol)
    - company=tenant => tenant kapsamı
    """
    party = models.ForeignKey('parties.Party', on_delete=models.CASCADE, related_name="roles")
    role  = models.ForeignKey('parties.Role', on_delete=models.CASCADE, related_name="party_roles")
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, null=True, blank=True,
                                related_name="party_roles")

    valid_from = models.DateField(default=timezone.now)
    valid_to   = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            # Aynı kapsam içinde aynı party+role bir kez
            models.UniqueConstraint(
                fields=["party", "role", "company"],
                name="uq_party_role_unique_in_scope",
            )
        ]
        indexes = [
            models.Index(fields=["company", "role"]),
            models.Index(fields=["party", "role"]),
        ]

    def clean(self):
        # Tenant kapsamı ise company zorunlu; platform ise company None
        if self.company_id is None and self.party.company_id is not None:
            # party tenant iken role platform olarak atanabilir mi? İstemezsek engelleriz.
            # İzin vermek istersen bu bloğu kaldırabilirsin.
            raise ValidationError("Tenant partisine platform kapsamlı rol atanamaz (company is None).")
        if self.company_id is not None:
            if self.party.company_id is not None and self.party.company_id != self.company_id:
                raise ValidationError("Party ile PartyRole aynı tenant içinde olmalı.")
        return super().clean()

    def __str__(self):
        scope = "platform" if self.company_id is None else self.company_id
        return f"{self.party} • {self.role.code} @ {scope}"


# ------- İlişkiler

class RelationshipType(models.Model):
    """
    owns / administrates / contract-with ... gibi tip sözlüğü
    """
    code = models.SlugField(max_length=50, unique=True)  # 'owns'
    name = models.CharField(max_length=100)              # 'Sahiplik'
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    """
    from_party --(type, from_role -> to_role)--> to_party
    İlişkinin bağlamı (company=None => platform, company=X => tenant X).
    """
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, null=True, blank=True,
                                related_name="party_relationships")

    type = models.ForeignKey('parties.RelationshipType', on_delete=models.PROTECT, related_name="relationships")
    from_party = models.ForeignKey('parties.Party', on_delete=models.CASCADE, related_name="rels_from")
    to_party   = models.ForeignKey('parties.Party', on_delete=models.CASCADE, related_name="rels_to")
    from_role  = models.ForeignKey('parties.Role', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="rels_from_as_role")
    to_role    = models.ForeignKey('parties.Role', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="rels_to_as_role")

    valid_from = models.DateField(default=timezone.now)
    valid_to   = models.DateField(null=True, blank=True)
    note       = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "type"]),
            models.Index(fields=["company", "from_party"]),
            models.Index(fields=["company", "to_party"]),
        ]

    def clean(self):
        # Kapsam kuralları: tenant ilişkisi ise tarafların da aynı tenantta olması beklenir
        if self.company_id is not None:
            # from_party ve to_party tenantları company ile uyumlu olmalı (ya aynı tenant ya da None ise kabul etme)
            if self.from_party.company_id not in (None, self.company_id):
                raise ValidationError("from_party bu tenantta değil.")
            if self.to_party.company_id not in (None, self.company_id):
                raise ValidationError("to_party bu tenantta değil.")
        else:
            # platform ilişkisi: tarafların company'leri None olabilir; varsa platform kapsamını bozmaz,
            # ama genellikle platform party'leri company=None olarak tanımlamanı öneririm.
            pass
        return super().clean()

    def __str__(self):
        return f"{self.from_party} —{self.type.code}→ {self.to_party}"


# ------- Yetenekler (Capabilities)

class Capability(models.Model):
    """
    İnce taneli izin/yetenek: ör. manage_platform, manage_tenant, view_contracts...
    """
    code = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class RoleCapability(models.Model):
    """
    Bir rol hangi yetenekleri verir? Genellikle global tanım.
    """
    role = models.ForeignKey('parties.Role', on_delete=models.CASCADE, related_name="capabilities")
    capability = models.ForeignKey('parties.Capability', on_delete=models.CASCADE, related_name="roles")

    class Meta:
        unique_together = [("role", "capability")]

    def __str__(self):
        return f"{self.role.code} -> {self.capability.code}"


class PartyCapability(models.Model):
    """
    Bir party'ye doğrudan yetenek ataması.
    - company=None: platform kapsamı
    - company=X: tenant X kapsamı
    """
    party = models.ForeignKey('parties.Party', on_delete=models.CASCADE, related_name="capabilities")
    capability = models.ForeignKey('parties.Capability', on_delete=models.CASCADE, related_name="party_grants")
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, null=True, blank=True,
                                related_name="party_capabilities")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["party", "capability", "company"],
                name="uq_party_capability_in_scope",
            )
        ]

    def __str__(self):
        scope = "platform" if self.company_id is None else f"tenant:{self.company_id}"
        return f"{self.party} -> {self.capability.code} @ {scope}"


# ------- Yardımcı (isteğe bağlı)

def party_has_capability(party: 'Party', capability_code: str, company=None) -> bool:
    """
    Efektif yetenek kontrolü:
    - Doğrudan PartyCapability (platform + tenant)
    - Rol tabanlı: PartyRole -> RoleCapability
    """
    from django.db.models import Exists, OuterRef

    # 1) Doğrudan atama
    direct = PartyCapability.objects.filter(
        party=party, capability__code=capability_code
    ).filter(
        Q(company__isnull=True) | Q(company=company)
    ).exists()

    if direct:
        return True

    # 2) Rollerden gelen
    role_caps = RoleCapability.objects.filter(
        capability__code=capability_code
    ).values("role_id")

    roles = PartyRole.objects.filter(party=party, role_id__in=role_caps)

    if company is None:
        roles = roles.filter(company__isnull=True)  # platform rolleri
    else:
        roles = roles.filter(Q(company=company) | Q(company__isnull=True))
        # tenant kapsamı + platformdan gelen roller

    return roles.exists()
