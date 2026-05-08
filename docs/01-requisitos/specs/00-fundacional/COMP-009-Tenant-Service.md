# COMP-009 — Tenant Service

## Metadata

- **Nombre**: tenant-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8002
- **DB**: PostgreSQL (schema `tenants`)
- **Servicios afectados**: todos los servicios internos
- **Componentes relacionados**: auth-service, sedes-service, billing-service

---

## Objetivo

Gestionar el ciclo de vida completo de los tenants (clientes SaaS): registro, activación, suspensión, migración de planes, y configuración. Cada tenant tiene configuración aislada de planes, billing, y preferencias.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 15
- **Cache**: Redis (datos de tenant, configuraciones)
- **Message Broker**: Kafka (eventos de tenant)
- **API**: REST + gRPC (interno)

---

## Modelo de Datos

### Tabla: tenants

```sql
id                  UUID PK
nombre              VARCHAR(255) NOT NULL
razon_social        VARCHAR(255)
nit                 VARCHAR(20) UNIQUE
email_contacto      VARCHAR(255) NOT NULL
telefono            VARCHAR(50)
direccion           TEXT
ciudad              VARCHAR(100)
pais                VARCHAR(100) DEFAULT 'CO'

plan                VARCHAR(50) NOT NULL  -- starter, professional, enterprise
estado              VARCHAR(20) DEFAULT 'trial'  -- trial, active, suspended, cancelled

trial_expires_at    TIMESTAMPTZ
subscription_id     UUID FK → subscriptions (nullable)

max_sedes           INTEGER DEFAULT 1
max_usuarios        INTEGER DEFAULT 5
max_espacios        INTEGER DEFAULT 50

features_flags      JSONB DEFAULT '{}'  -- overrides de features por tenant

settings            JSONB DEFAULT '{}'  -- preferencias, timezone, currency

stripe_customer_id  VARCHAR(255)
diand_client_id     VARCHAR(255)  -- DIAN credentials

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
activated_at        TIMESTAMPTZ
suspended_at        TIMESTAMPTZ
cancelled_at        TIMESTAMPTZ
```

### Tabla: subscriptions

```sql
id                  UUID PK
tenant_id           UUID FK → tenants

plan                VARCHAR(50) NOT NULL
price_monthly       DECIMAL(10,2)
price_yearly        DECIMAL(10,2)
currency            VARCHAR(3) DEFAULT 'COP'

status              VARCHAR(20)  -- active, past_due, cancelled, paused

current_period_start TIMESTAMPTZ
current_period_end  TIMESTAMPTZ

stripe_subscription_id  VARCHAR(255)
stripe_price_id        VARCHAR(255)

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: tenant_events

```sql
id                  UUID PK
tenant_id           UUID FK → tenants
event_type          VARCHAR(50) NOT NULL  -- created, activated, suspended, plan_changed, cancelled
metadata            JSONB DEFAULT '{}'
created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: tenant_config

```sql
id                  UUID PK
tenant_id           UUID FK → tenants UNIQUE

notification_channels JSONB DEFAULT '{"email": true, "push": true}'
alert_thresholds       JSONB DEFAULT '{"mora_horas": 24, "ocupacion_min": 20}'
tarifa_default_minutos INTEGER DEFAULT 60
currency              VARCHAR(3) DEFAULT 'COP'
timezone              VARCHAR(50) DEFAULT 'America/Bogota'

custom_branding      JSONB  -- logo, colors, company name

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints REST

### GET /api/v1/tenants
Lista todos los tenants (superadmin only).
```json
{
  "tenants": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### POST /api/v1/tenants
Crea nuevo tenant (registro o trial).
```json
{
  "nombre": "string",
  "email_contacto": "string",
  "plan": "starter|professional|enterprise"
}
```

### GET /api/v1/tenants/{tenant_id}
Obtiene detalles del tenant.

### PATCH /api/v1/tenants/{tenant_id}
Actualiza datos del tenant (no plan).

### POST /api/v1/tenants/{tenant_id}/activate
Activa tenant (convierte trial → active).

### POST /api/v1/tenants/{tenant_id}/suspend
Suspende tenant (falta de pago, etc).
```json
{
  "reason": "payment_failed",
  "days_until_cancellation": 30
}
```

### POST /api/v1/tenants/{tenant_id}/reactivate
Reactiva tenant suspendido.

### DELETE /api/v1/tenants/{tenant_id}
Cancela tenant (soft delete, no hard delete).

### POST /api/v1/tenants/{tenant_id}/plan
Cambia plan (upgrade/downgrade).
```json
{
  "new_plan": "professional",
  "prorate": true
}
```

### GET /api/v1/tenants/{tenant_id}/config
Obtiene configuración del tenant.

### PATCH /api/v1/tenants/{tenant_id}/config
Actualiza configuración.

### GET /api/v1/tenants/{tenant_id}/usage
Uso actual vs límites.
```json
{
  "sedes": { "used": 3, "max": 5 },
  "usuarios": { "used": 12, "max": 10 },
  "espacios": { "used": 150, "max": 200 }
}
```

---

## Endpoints gRPC (interno)

```protobuf
service TenantService {
  rpc GetTenant(GetTenantRequest) returns (Tenant);
  rpc ListTenants(ListTenantsRequest) returns (ListTenantsResponse);
  rpc CheckPlanLimit(CheckLimitRequest) returns (CheckLimitResponse);
  rpc GetTenantConfig(GetConfigRequest) returns (TenantConfig);
}
```

---

## Plan Features

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Max sedes | 1 | 5 | Unlimited |
| Max usuarios | 5 | 25 | Unlimited |
| Max espacios | 50 | 500 | Unlimited |
| Analytics | Basic | Advanced | Advanced + custom |
| API rate limit | 60 rpm | 300 rpm | 1000 rpm |
| Soporte | Email | Email + chat | Dedicated |
| Custom branding | No | Yes | Yes |
| SSO | No | No | Yes |
| Audit log retention | 7 days | 30 days | 90 days |
| Multi-tenant billing | No | No | Yes |

---

## Rate Limiting por Plan

| Plan | Límite |
|------|--------|
| Starter | 60 rpm |
| Professional | 300 rpm |
| Enterprise | 1000 rpm |

---

## Eventos Kafka

### Topic: `parkcore.tenants`

```json
{
  "event_type": "tenant.created",
  "tenant_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "data": {
    "nombre": "...",
    "plan": "...",
    "email_contacto": "..."
  }
}
```

Eventos:
- `tenant.created`
- `tenant.activated`
- `tenant.suspended`
- `tenant.reactivated`
- `tenant.plan_changed`
- `tenant.cancelled`
- `tenant.config_updated`

---

## Flujo de Creación de Tenant

```
1. POST /tenants (trial)
   ├── Crear tenant en DB (estado = trial)
   ├── Crear subscription (stripe customer)
   ├── Enviar email de bienvenida
   └── Publicar evento tenant.created

2. Activation (POST /tenants/{id}/activate)
   ├── Validar datos de facturación
   ├── Activar subscription en Stripe
   ├── Crear sede inicial por defecto
   └── Publicar evento tenant.activated

3. Trial → Active (cron job diario)
   ├── Si trial_expires_at < hoy AND subscription not activated
   └── Suspender tenant, notificar
```

---

## Flujo de Cambio de Plan

```
1. POST /tenants/{id}/plan { new_plan: "professional" }
2. Validar límites (max_sedes, max_usuarios, max_espacios)
3. Si downgrade:
   └── Verificar que uso actual < nuevos límites
4. Llamar Stripe API para cambiar price
5. Actualizar tenant.plan y subscription
6. Ajustar features_flags según nuevo plan
7. Publicar evento tenant.plan_changed
8. Enviar email confirmación
```

---

## Dependencias

- **DB**: PostgreSQL `tenants` schema
- **Redis**: Cache de tenant data (TTL 5min)
- **Kafka**: Eventos de tenant
- **Stripe**: Suscripciones y pagos
- **DIAN**: Configuración facturación electrónica
- **Vault**: Secrets de APIs externas

---

## Métricas

- `tenant_created_total{plan="..."}`
- `tenant_activated_total`
- `tenant_suspended_total{reason="..."}`
- `tenant_plan_changed_total{from_plan, to_plan}`
- `tenant_active_gauge{plan="..."}`
- `subscription_mrr{plan="..."}` (Monthly Recurring Revenue)

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "kafka": "connected" }
GET /health/ready → verifica DB y cache
GET /health/live → solo proceso activo
```

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Trial expira sin pago | Suspender tenant, envío email con grace period 7 días |
| Downgrade con uso excedido | Error 422 con mensaje "Límites excedidos para plan {plan}" |
| Stripe webhook failure | Retry con exponential backoff (max 24h) |
| NIT duplicado | Error 409 con mensaje "Ya existe un tenant con este NIT" |
| Cancelación con espacios activos | Error 400 "No se puede cancelar: hay espacios en uso" |

---

## Notas

- Soft delete: tenants cancelled no se eliminan, estado = cancelled
- DN/CI lookup en background para validar NIT colombiano
- Multi-tenant isolation enforced at DB level (tenant_id en todos los queries)
- El campo `features_flags` permite overrides para clientes enterprise
- Zona horaria del tenant afectadisplay de horas en dashboard