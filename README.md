# Tema CAM (backend)
## Continuous Auditing Module Developed by Tema Tech

### Features

- Multi Tenant
- SQL Based Rule Engine 
- Control Library
- Alert Lifecyle 
- Managerial Dashboards
- Modern UI/UX

## Üst Düzey Mimari

Proje: config (settings, urls, asgi/wsgi)

### Çekirdek uygulamalar:

1. apps.core (ortak yardımcılar, base models, audit trail, timezones, money)
2. apps.tenants (Tenant, Domain, planlama/limitler;)
3. apps.parties (Party, PartyRole, PartyRelationship; kişi, şirket, kamu, sistem vb.)
4. apps.rules (kural motoru; DSL veya Python tabanlı koşullar)
5. apps.audit (CCM/sürekli denetim: Control, Test, Evidence, Finding, Case/Workflow)
6. apps.connectors (UBL-TR, e-Fatura/e-Arşiv, e-Defter, banka ekstreleri, POS, ERP dış kaynak)

### Muhasebe domaini (ayrı app’ler):

7. apps.ledger (Hesap Planı, Yevmiye, Defter-i Kebir, dönem kapanış)
8. apps.ar (Alacak/Borçlu müşteri; tahsilat, dekontlar)
9. apps.ap (Tedarikçi borçları; ödeme, masraf, satınalma)
10. apps.billing (Faturalama; UBL-TR jenerasyonu/parse)
11. apps.cashbank (Kasa, banka, ekstre mutabakatı)
12. apps.inventory (Opsiyonel: stok, giriş/çıkış, maliyet)
13. apps.fixedassets (Opsiyonel: sabit kıymet, amortisman)

### Kullanıcı Arayüzü:

Her uygulama kendi templates klasörünü yönetir (namespaced).

14. apps.workspace (giriş/çalışma alanı, dashboard’lar, çok-tenant switcher)
15. apps.notifications (e-posta, web push, sistem uyarıları)
