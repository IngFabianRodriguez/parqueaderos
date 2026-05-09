# SPEC-07-035 — Suspensión de Tenant por Falta de Pago

## Metadata
- **RF origen**: RF-035
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, tenant-service, notification-service, api-gateway

---

## User Story
**Como** administrador de ParkCore **quiero** que los tenants que no paguen su suscripción pasen a modo solo lectura **para** proteger los ingresos de la plataforma y motivar el pago sin perder al cliente definitivamente.

## Objetivo
El sistema debe cambiar el estado de un tenant a suspended cuando el pago de su suscripción falle después de agotar los reintentos, restringiendo su acceso a operaciones de escritura mientras mantiene sus datos disponibles para lectura.

## Comportamiento Específico

### Happy Path
1. Stripe intenta cobrar la renovación mensual y falla
2. Stripe reintenta a las 24h, 48h y 72h (3 intentos)
3. Después del tercer intento fallido, Stripe envía webhook invoice.payment_failed
4. Sistema actualiza: status = suspended, suspended_at = NOW(), suspension_reason = payment_failed
5. El acceso a operaciones POST/PUT/DELETE se bloquea; GET sigue funcionando
6. Dashboard muestra banner de suspensión con botón "Pagar ahora"
7. Al recibir pago exitoso, estado vuelve a active

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tenant suspendido intenta registrar entrada | Retornar 403 "Tu cuenta está suspendida" |
| Tenant suspendido accede a dashboard | Datos se muestran en modo lectura; banner de suspensión prominente |
| Pago realizado pero webhook no llega | Sistema hace polling a Stripe API cada 5 min |
| Tenant suspendido por > 30 días | Se considera churn |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| reason | enum | Motivo: payment_failed, manual, compliance | Sí |
| stripe_invoice_id | string | ID de la factura pendiente | Sí (automático) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| status | enum | suspended |
| suspended_at | datetime | Timestamp de suspensión |
| suspension_reason | string | Motivo detallado |
| days_since_suspension | integer | Días transcurridos desde la suspensión |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant sin pago después de 3 reintentos en 7 días pasa a estado suspended automáticamente
2. En estado suspended, las operaciones POST/PUT/DELETE retornan 403
3. Las operaciones GET (lectura) siguen funcionando
4. El banner de suspensión es visible en todas las páginas hasta que se reactive
5. La reactivación ocurre dentro de los 5 segundos posteriores al webhook de pago exitoso

## Endpoints
- `POST /api/v1/webhooks/stripe` — Recibir invoice.payment_failed (dispara suspensión)
- `POST /api/v1/webhooks/stripe` — Recibir invoice.payment_succeeded (dispara reactivación)
- `GET /api/v1/tenants/{tenant_id}/status` — Consultar estado

## Health Check
- `GET /health` → { "status": "ok" }