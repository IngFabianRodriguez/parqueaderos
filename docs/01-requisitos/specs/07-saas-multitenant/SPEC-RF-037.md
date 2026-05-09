# SPEC-07-037 — Selección de Plan de Suscripción

## Metadata
- **RF origen**: RF-037
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, tenant-service, plan-service

---

## User Story
**Como** administrador de un tenant **quiero** ver y seleccionar un plan de suscripción adecuado a mis necesidades **para** acceder a las funcionalidades que mi negocio requiere.

## Objetivo
El sistema debe presentar los planes de suscripción disponibles (Starter, Professional, Enterprise, Custom) con sus características, precios y límites, permitiendo al tenant_admin seleccionar y contratar el plan que mejor se ajuste a sus necesidades.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Suscripción > "Cambiar plan"
2. Sistema muestra comparativa de planes: Starter, Professional, Enterprise, Custom
3. Tenant compara planes y hace clic en "Suscribirse" en el plan elegido
4. Sistema redirige al Stripe Checkout
5. Al confirmar el pago, Stripe envía webhook payment_succeeded
6. Sistema actualiza la suscripción con el nuevo plan
7. Sistema activa los feature flags del nuevo plan

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Upgrade desde trial | Plan se activa inmediatamente; se cobra el precio completo |
| Upgrade de Starter a Professional | Prorrateo el día del upgrade; se cobra la diferencia |
| Pago falla durante checkout | Tenant permanece en plan actual |
| Plan Custom solicitado | Se guarda request; equipo de ventas contacta al tenant |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| plan_selected | enum | Plan elegido (starter, professional, enterprise, custom) | Sí |
| billing_cycle | enum | Ciclo de facturación (monthly, annual) | Sí |
| custom_plan_details | JSON | Detalles de necesidades para plan Custom | Sí (Custom) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| plan | string | Plan activo del tenant |
| price | decimal | Precio mensual del plan |
| billing_cycle | string | Ciclo de facturación |
| features | array | Lista de features activas para el plan |
| limits | object | Límites del plan (sedes, usuarios, transacciones) |
| next_billing_date | datetime | Fecha del próximo cobro |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. La página de selección de planes muestra todos los planes disponibles con sus precios y features
2. El tenant puede seleccionar monthly o annual; el precio annual muestra descuento del 20%
3. Al seleccionar un plan, el tenant ve inmediatamente los feature flags actualizados
4. Si el tenant intenta usar más sedes de las que su plan permite, recibe error 403 con upgrade prompt

## Endpoints
- `GET /api/v1/plans` — Listar planes disponibles
- `GET /api/v1/plans/{plan_id}` — Detalle de un plan
- `POST /api/v1/subscriptions/create-checkout` — Crear Stripe Checkout session
- `GET /api/v1/tenants/{tenant_id}/subscription` — Consultar suscripción actual

## Health Check
- `GET /health` → { "status": "ok" }