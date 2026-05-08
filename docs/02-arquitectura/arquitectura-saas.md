# Arquitectura SaaS — ParkCore

## Contexto

ParkCore se diseñó desde el inicio para ser un **SaaS multi-tenant** donde cada cliente de la plataforma (empresa, franquicia, o propietario individual de parqueaderos) opera en su propio espacio aislado. Este documento describe cómo se estructuran la tenantencia, facturación de suscripciones, personalización por marca, gestión de usuarios por organización y el modelo de datos que soporta la operación SaaS completa.

---

## 1. Modelo de Tenantencia

### 1.1 Jerarquía de Organizaciones

```
Tenant (cuenta SaaS)
├── Usuarios propios (team del cliente)
├── Suscripción activa
├── Configuración de marca (logo, colores, dominio)
├── Módulo de facturación propio
└── Sede(s) — una o muchas
    ├── Zonas
    ├── Espacios
    ├── Dispositivos IoT
    └── Operadores propios
```

**Definiciones clave:**

- **Tenant**: Entidad jurídica o empresa que contrata ParkCore. Representa una cuenta SaaS con facturación独立iente.
- **Sede**: Cada parqueadero físico. Una sede pertenece a un único tenant. Un tenant puede tener de 1 a N sedes.
- **Usuario**: Personas del equipo del tenant que acceden al sistema. Cada usuario pertenece a un tenant específico.
- **Operador**: Usuario con rol de_OPERADOR en una sede específica.

### 1.2 Aislamiento de Datos

> **Regla de oro**: Un tenant nunca puede ver datos de otro tenant. Todo query incluye `tenant_id` como filtro obligatorio, enforced a nivel de ORM/middleware.

```python
# Ejemplo: todos los queries del ORM incluyen tenant_id automáticamente
class BaseModel(DeclarativeBase):
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenant.id"), nullable=False)

    __mapper_args__ = {"inherit_cache": False}

# Middleware que inyecta tenant_id en cada request
class TenantMiddleware:
    async def __call__(self, scope, receive, send):
        token = extract_jwt(scope)
        tenant_id = token["tenant_id"]  # extraído del JWT
        scope["tenant_id"] = tenant_id
```

### 1.3 Modelos de Tenant (esquema de base de datos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | PK del tenant |
| nombre | VARCHAR(200) | Razón social o nombre de la empresa |
| slug | VARCHAR(100) | URL única (parkcore.io/{slug}) |
| tipo | VARCHAR(20) | `trial`, `active`, `suspended`, `churned` |
| plan_id | UUID | FK → subscription_plan |
| fecha_contrato | DATE | Inicio del contrato |
| fecha_renovacion | DATE | Próxima facturación |
| billing_email | VARCHAR(255) | Email para facturas |
| branding_enabled | BOOLEAN | Si tiene branding personalizado |
| custom_domain | VARCHAR(255) | Dominio propio (opcional) |
| metadata | JSONB | Configuración flexible |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## 2. Suscripciones y Facturación SaaS

### 2.1 Planes de Suscripción

| Plan | Precio base | Sedes incluidas | Transacciones/mes | Features |
|------|------------|-----------------|-------------------|----------|
| **Starter** | $99.000/mes | 1 sede | 500 | Dashboard básico, ANPR, pagos básicos |
| **Professional** | $299.000/mes | 3 sedes | 2.000 | Multi-sede, app operador, reportes, CRM |
| **Enterprise** | $799.000/mes | 10 sedes | 10.000 | Todo + BI avanzado, API abierta, SSO, SLA 99.9% |
| **Custom** | Negociable | Ilimitado | Ilimitado | White-label, infra dedicada, soporte 24/7 |

### 2.2 Modelo de Precios por Usage (Usage-Based Billing)

Además del plan fijo, sefactura por uso excedente:

```
Transacciones incluidas en plan:
  Starter: 500/mes
  Professional: 2.000/mes
  Enterprise: 10.000/mes

Excedente:
  $200 COP por transacción adicional
  Facturado al cierre del ciclo de facturación

Métricas trackeadas por tenant:
  - transacciones_totales: contador mensual
  - sedes_activas: gauge (para plan por sede)
  - vehiculos_registrados: gauge
  - api_calls_externos: contador (para plan API)
  - almacenamiento_gb: gauge (fotos ANPR)
```

### 2.3 Ciclo de Facturación

```
Ciclo: Mensual (el día de renovación)
Día de facturación: Fecha de contratación (ej: día 15)

Flujo:
1. D-5: Se calcular el uso del mes (transacciones, sedes extras)
2. D-1: Se genera invoice preview en Stripe
3. D+0: Se cobra automáticamente
   - Si OK: Tenant sigue activo
   - Si falla: Se intenta 3 veces (D+1, D+3, D+7)
   - Si fallan los 3 intentos: Tenant pasa a `suspended`
4. D+8: Se notifica al admin, acceso restringido (solo lectura)
5. D+30: Tenant pasa a `churned`, datos se retienen 90 días
```

### 2.4 Estados de Suscripción

```
                    ┌──────────────┐
                    │   trial      │ ← 14 días, sin cobrar
                    └──────┬───────┘
                           │ conversión exitosa
                           ▼
                    ┌──────────────┐
                    │   active     │ ← pago exitoso
                    └──────┬───────┘
                           │ falla de pago
                    ┌──────▼───────┐
              ┌─────│  suspended   │ ← read-only, 8 días para resolver
              │     └──────┬───────┘
              │            │ resuelto en 8 días
              │            ▼
              │     ┌──────────────┐
              │     │   active    │
              │     └──────────────┘
              │
              │ no resuelto en 30 días
              ▼
       ┌──────────────┐
       │  churned     │ ← datos retenidos 90 días, luego eliminación
       └──────────────┘
```

### 2.5 Gestión de Plan (Upgrade / Downgrade)

- **Upgrade**: Inmediato, prorrateo del mes en curso, cobra la diferencia
- **Downgrade**: Al final del ciclo de facturación actual (no prorrateo)
- **Cancelación**: Al final del ciclo, el tenant recibe un email de confirmación y pierde acceso al sistema al día siguiente

### 2.6 Integración con Stripe (Billing Engine)

```
Tenant paga → Stripe
           → Subscription criada en Stripe (no en nuestra BD)
           → Webhook de Stripe nos actualiza el estado
           → Generamos invoice interno para el cliente
```

**Stripe webhooks manejados:**

| Evento | Ação en ParkCore |
|--------|-----------------|
| `invoice.paid` | Suscripción activa, reset contador usage |
| `invoice.payment_failed` | Suspensión temporal, envío de email |
| `customer.subscription.updated` | Actualizar plan en tenant |
| `customer.subscription.deleted` | Marcar como churned |
| `usage_record.created` | Incrementar contador de transacciones |

### 2.7 Dunning (Reintento de Pago)

```
Intento 1 (D+0): Falla → email inmediato al admin
Intento 2 (D+1): Falla → email con urgencia + banner en dashboard
Intento 3 (D+3): Falla → email final + link de actualización de método de pago
Intento 4 (D+7): Falla → Suspender cuenta (read-only)
D+30: Cancelación definitiva → churned
```

---

## 3. Módulo de Brand & White-Label (Personalización por Tenant)

### 3.1 Elementos Personalizables por Tenant

Cada tenant puede personalizar la experiencia visual para sus operadores y clientes:

| Elemento | Starter | Professional | Enterprise | Custom |
|----------|---------|--------------|------------|--------|
| Logo en dashboard | ✓ | ✓ | ✓ | ✓ |
| Color primario/secondary | ✗ | ✓ | ✓ | ✓ |
| Favicon personalizado | ✗ | ✓ | ✓ | ✓ |
| Email branding (desde address) | ✗ | ✓ | ✓ | ✓ |
| Dominio personalizado | ✗ | ✗ | ✓ | ✓ |
| App móvil white-label | ✗ | ✗ | ✗ | ✓ |
| Nombre del producto renombrado | ✗ | ✗ | ✗ | ✓ |

### 3.2 Configuración de Branding en BD

```sql
CREATE TABLE tenant_branding (
    tenant_id       UUID PRIMARY KEY REFERENCES tenant(id),
    logo_url        VARCHAR(500),        -- S3 URL del logo
    favicon_url     VARCHAR(500),
    primary_color   VARCHAR(7),          -- #RRGGBB
    secondary_color VARCHAR(7),
    custom_fonts    JSONB,               -- { "heading": "Roboto", "body": "Open Sans" }
    email_from_name VARCHAR(100),        -- "Parqueadero Los Andes"
    email_from_address VARCHAR(255),     -- "no-reply@parqueaderoslosandes.com"
    custom_domain   VARCHAR(255),        -- "app.parqueaderoslosandes.com"
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.3 Custom Domain (Enterprise+)

El tenant enterprise puede usar su propio dominio:

1. CNAME en DNS: `app.cliente.com → cname.parkcore.io`
2. ParkCore provee certificado SSL automáticamente (Let's Encrypt)
3. El API Gateway routing based on Host header

```yaml
# Kong config para custom domains
services:
  - name: tenant-router
    url: http://tenant-router-service:8009
    routes:
      - name: custom-domain-route
        hosts:
          - "app.cliente1.com"
          - "app.cliente2.com"
        strip_path: false
```

---

## 4. Gestión de Usuarios y Permisos por Tenant

### 4.1 Estructura de Usuarios

```
Tenant
├── Admin (1+): puede gestionar usuarios, facturacion, sedes
├── Manager (0+): gestiona operaciones de sus sedes asignadas
├── Operador (0+): opera en piso (una o más sedes)
└── Viewer (0+): solo lectura de reportes
```

### 4.2 Roles por Defecto

| Rol | Sedes | Permisos clave |
|-----|-------|----------------|
| `tenant_admin` | Todas | Todo incluido billing, usuarios, upgrades |
| `sede_manager` | Asignadas | Operadores, reportes, config de sede |
| `sede_operator` | Asignadas | Abrir talanqueras, ver dashboard, incidentes |
| `viewer` | Todas o asignadas | Solo lectura |

### 4.3 Users Table (Multi-tenant)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID NOT NULL REFERENCES tenant(id),
    email          VARCHAR(255) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    nombre         VARCHAR(100) NOT NULL,
    rol            VARCHAR(50) NOT NULL,
    estado         VARCHAR(20) DEFAULT 'activo',
    ultimo_acceso   TIMESTAMPTZ,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado_hasta TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email_tenant ON users(tenant_id, email);
```

### 4.4 SSO / SAML (Enterprise)

Para tenants enterprise que requieren SSO corporativo:

```
Empresa usa Okta / Azure AD / Google Workspace
    │
    ├─── SAML assertion ──→ ParkCore valida contra IdP
    │
    ├─── Usuario existe? → No: crear en tenant (just-in-time provisioning)
    │
    └─── Rol? → mapear a roles ParkCore según atributo del IdP
```

**Endpoints SAML:**
- `GET /auth/saml/{tenant_slug}/login`
- `POST /auth/saml/{tenant_slug}/acs` (Assertion Consumer Service)
- `GET /auth/saml/{tenant_slug}/metadata` (SP metadata)

---

## 5. API Keys para Integraciones por Tenant

### 5.1 API Keys como Mecanismo de Acceso Externo

Cada tenant puede generar API keys para que aplicaciones de terceros se integren:

```
Tenant quiere que:
- App de mapas (Waze) consulte disponibilidad
- App de reservas de terceros cree reservas
- ERP del cliente lea transacciones
```

### 5.2 API Key Lifecycle

```
Crear → Rotar → Revocar
```

**Tabla de API keys:**

```sql
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID NOT NULL REFERENCES tenant(id),
    nombre          VARCHAR(100) NOT NULL,          -- "Integración Waze"
    key_hash        VARCHAR(255) NOT NULL,          -- SHA-256 del key value
    key_prefix      VARCHAR(8) NOT NULL,            -- Primeros 8 chars para identificar
    scopes          JSONB NOT NULL,                 -- ["disponibilidad:read", "reservas:write"]
    expires_at      TIMESTAMPTZ,                   -- NULL = nunca expira
    last_used_at    TIMESTAMPTZ,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ,
    UNIQUE (tenant_id, nombre)
);
```

**Generación de key:**
```
pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
│ │    │
│ │    └── 32 bytes aleatorios (mostrados solo en creación)
│ └── prefix (para identificar la key en UI)
└── prefijo fixed ("pk_live_" o "pk_test_")
```

### 5.3 Rate Limiting por API Key

```
Límite por tier:
  Starter: 100 requests/min
  Professional: 500 requests/min
  Enterprise: 2.000 requests/min

Rate limit headers en respuestas:
  X-RateLimit-Limit: 500
  X-RateLimit-Remaining: 487
  X-RateLimit-Reset: 1622534400
```

---

## 6. Onboarding de Nuevo Tenant

### 6.1 Flujo de Registro

```
1. Usuario llega a parkcore.io y hace clic en "Comenzar prueba"
2. Ingresa: nombre empresa, email, contraseña
3. Se crea Tenant en estado "trial" (14 días gratis)
4. Se crea Stripe Customer (sin subscription todavía)
5. Email de bienvenida enviado
6. Wizard de onboarding:
   a) Datos de la empresa (NIT, dirección, ciudad)
   b) Crear primera sede (nombre, dirección, capacidad)
   c) Configurar sensores (opcional, puede hacer después)
   d) Invitar al equipo (opcional)
7. Dashboard de la primera sede listo para usar
```

### 6.2 Wizard de Primera Sede

```
Step 1: Datos de la sede
  - Nombre
  - Dirección (geocodificada automáticamente)
  - Ciudad
  - Capacidad total (número de espacios)
  - Horario de operación

Step 2: Zonas (opcional)
  - Crear zonas: VIP, Cubierta, Descubierta, Moto
  - Asignar tarifa a cada zona

Step 3: Talanqueras
  - Entrada y/o salida
  - Configuración IP (para MQTT)

Step 4: Sensores (opcional)
  - Tipo de sensor por zona
  - Configuración de gateway

Step 5: Invitar equipo
  - Emails de operadores
  - Roles asignados
```

---

## 7. Métricas SaaS (Business Metrics)

### 7.1 KPIs de Suscripción

```python
# Métricas calculadas mensualmente para reporting interno

MRR (Monthly Recurring Revenue):
  suma de ingresos recurrentes del mes actual

ARR (Annual Recurring Revenue):
  MRR × 12

Churn Rate:
  tenants perdidos en el mes / total tenants inicio de mes
  Target: < 2% mensual

NRR (Net Revenue Retention):
  Ingresos de tenants existentes mes actual / ingresos mismos tenants mes pasado
  Target: > 110% (expansión > churn)
  Includes: upgrades, cross-sell, menos churn y downgrade

LTV (Lifetime Value):
  MRR promedio por tenant / Churn Rate mensual
  Ejemplo: MRR $200K, Churn 2% → LTV = $200K / 0.02 = $10M

CAC (Customer Acquisition Cost):
  Total spend en sales+marketing / Nuevos tenants adquiridos

CAC Payback:
  CAC / MRR por tenant
  Target: < 6 meses

Logo Churn:
  Número de tenants cancelados / Total tenants
```

### 7.2 Tablas para Tracking

```sql
-- Métricas mensuales calculadas y almacenadas
CREATE TABLE saas_metrics (
    id              UUID PRIMARY KEY,
    tenant_id       UUID REFERENCES tenant(id),  -- NULL para métricas agregadas
    mes             DATE NOT NULL,               -- Primer día del mes
    mrr_cents       BIGINT,                       -- En centavos para evitar decimals
    arr_cents       BIGINT,
    seats_count     INTEGER,
    transacciones_count INTEGER,
    churned         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Eventos significativos de suscripciones
CREATE TABLE subscription_events (
    id              UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    tipo            VARCHAR(50) NOT NULL,        -- trial_started, converted, upgraded, downgraded, churned, payment_failed
    plan_id         UUID,
    monto_cop       BIGINT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 8. Feature Flags por Plan

### 8.1 Matriz de Features por Plan

| Feature | Starter | Professional | Enterprise | Custom |
|---------|---------|--------------|------------|--------|
| Múltiples sedes | ✗ | ✓ (3) | ✓ (10) | ✓ |
| App operador móvil | ✗ | ✓ | ✓ | ✓ |
| Dashboard BI | ✗ | ✗ | ✓ | ✓ |
| API access | ✗ | ✓ | ✓ | ✓ |
| SSO / SAML | ✗ | ✗ | ✓ | ✓ |
| White-label app | ✗ | ✗ | ✗ | ✓ |
| Custom domain | ✗ | ✗ | ✓ | ✓ |
| Multi-factor auth | ✓ | ✓ | ✓ | ✓ |
| Roles custom | ✗ | ✗ | ✓ | ✓ |
| Auditoria logs | ✓ (30 días) | ✓ (90 días) | ✓ (1 año) | ✓ |
| Soporte | Email | Email + Chat | Priority + Phone | Dedicado |
| SLA | 99.5% | 99.5% | 99.9% | Custom |

### 8.2 Implementación de Feature Flags

```python
# Middleware que inyecta features disponibles del tenant en cada request
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_tenant_features(tenant_id: UUID) -> dict:
    plan = db.get_plan_for_tenant(tenant_id)
    return FEATURE_MATRIX[plan]

# Uso en código
def endpoint_disponibilidad():
    if not get_tenant_features(tenant_id)["bi_advanced"]:
        raise Forbidden("Upgrade to Enterprise for BI")
```

```python
# Matriz de features por plan
FEATURE_MATRIX = {
    "starter": {
        "multi_sede": False,
        "app_operador": False,
        "bi_advanced": False,
        "api_access": True,
        "sso": False,
        "white_label": False,
        "custom_domain": False,
        "mfa": True,
        "audit_logs_days": 30,
        "soporte": "email",
        "sla": 99.5,
    },
    "professional": {
        "multi_sede": True,
        "sedes_max": 3,
        "app_operador": True,
        "bi_advanced": False,
        "api_access": True,
        "sso": False,
        "white_label": False,
        "custom_domain": False,
        "mfa": True,
        "audit_logs_days": 90,
        "soporte": "email_chat",
        "sla": 99.5,
    },
    "enterprise": {
        "multi_sede": True,
        "sedes_max": 10,
        "app_operador": True,
        "bi_advanced": True,
        "api_access": True,
        "sso": True,
        "white_label": False,
        "custom_domain": True,
        "mfa": True,
        "audit_logs_days": 365,
        "soporte": "priority",
        "sla": 99.9,
    },
    "custom": { ... }
}
```

---

## 9. Estructura de Servicios para SaaS

### 9.1 Nuevos Servicios

```
┌─────────────────────────────────────────────────────────────┐
│                      EXISTING SERVICES                      │
│  auth | sedes | iot | pagos | notif | anpr                 │
└─────────────────────────────────────────────────────────────┘
                          + NEW SERVICES
                                │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
┌───┴───┐             ┌──────┴──────┐          ┌──────┴──────┐
│tenant-│             │ billing-    │          │ brand-      │
│service│             │ service     │          │ service     │
└───┬───┘             └──────┬──────┘          └──────┬──────┘
    │                         │                         │
    └─── PostgreSQL ──────────┴─────────────────────────┘
           (tenant schema)     Stripe             CDN (logos)
```

### 9.2 Servicio: tenant-service (8007)

Responsabilidades:
- CRUD de tenants
- Gestión de usuarios por tenant
- Feature flags por plan
- Onboarding flow
- SSO/SAML

### 9.3 Servicio: billing-service (8008)

Responsabilidades:
- Gestión de suscripciones en Stripe
- webhook handlers de Stripe
- Generación de invoices internos
- Tracking de MRR/ARR/churn
- Dunning management
- Usage tracking

### 9.4 Servicio: brand-service (8009)

Responsabilidades:
- Gestión de assets de marca (logos, colores)
- Custom domain routing
- Email templates personalizados

---

## 10. Checklist de Operación SaaS

Antes de lanzar a producción, verificar:

- [ ] Aislamiento de datos por tenant enforced en ORM (queries fallan si no hay tenant_id)
- [ ] Middleware de tenant injection en todas las requests
- [ ] Suscripciones creadas en Stripe al convertir trial
- [ ] Webhooks de Stripe implementados y testeados (incluyendo retry de Stripe)
- [ ] Feature flags funcionando correctamente
- [ ] Branding por tenant renderizando correctamente (dashboard, emails)
- [ ] API keys generables, revocables, con rate limits por tier
- [ ] Onboarding wizard completo y funcional
- [ ] Dunning flow testeado (3 intentos, suspensión, churn)
- [ ] Métricas SaaS calculándose correctamente (MRR, churn, NRR)
- [ ] SSO/SAML funciona con IdP de prueba
- [ ] Custom domain SSL provisioning automático
- [ ] Plan downgrade cancela features no incluidas al final del ciclo
- [ ] Datos de tenant churned retenidos 90 días, luego eliminados
- [ ] Migración de plan upgrade/downgrade no pierde data