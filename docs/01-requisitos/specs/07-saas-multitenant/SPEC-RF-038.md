# SPEC-07-038 — Cobro Automático del Plan Mensual

## Metadata
- **RF origen**: RF-038
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, stripe-integration, notification-service

---

## User Story
**Como** administrador de ParkCore **quiero** que el cobro de la suscripción de cada tenant se realice automáticamente el día de renovación **para** que el servicio no se interrumpa y no haya trabajo manual de cobros.

## Objetivo
El sistema debe cobrar automáticamente el plan de suscripción de cada tenant activo el día de renovación, usando Stripe como motor de cobros recurrentes, con manejo de fallos y reintentos integrados.

## Comportamiento Específico

### Happy Path
1. Cada día a las 00:00 UTC, el job de billing ejecuta la verificación de renovaciones
2. El job consulta Stripe para subscriptions con current_period_end = hoy
3. Para cada suscripción: Stripe intenta cobrar con el payment method guardado
4. Si el cobro es exitoso: Stripe genera invoice.paid, envía webhook invoice.payment_succeeded
5. Sistema recibe webhook; actualiza current_period_start y current_period_end
6. Sistema genera evento subscription_renewed
7. Sistema envía email de confirmación de renovación

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tarjeta vencida | Stripe rechaza el pago; reintentos fallidos llevan a suspensión |
| Fondos insuficientes | Igual al anterior |
| Método de pago no existe | Stripe no puede cobrar; se marca la suscripción como uncollectible |
| Cobro duplicado | Stripe ya tiene deduplicación por invoice_id |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| stripe_subscription_id | string | ID de la suscripción en Stripe | Sí |
| tenant_id | UUID | Tenant asociado | Sí |
| amount | decimal | Monto a cobrar | Calculado |
| currency | string | Moneda (COP) | Fijo |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| invoice_id | string | ID de la invoice en Stripe |
| amount_paid | decimal | Monto cobrado exitosamente |
| current_period_start | datetime | Nuevo inicio del periodo |
| current_period_end | datetime | Nueva fecha de fin del periodo |
| status | enum | active, past_due, canceled |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo tenant con suscripción activa se cobra automáticamente en su fecha de renovación
2. El cobro exitoso actualiza current_period_end sumando exactamente 1 mes o 1 año si es annual
3. La invoice de Stripe se genera y está disponible para descarga
4. El email de confirmación se envía dentro de los 5 minutos posteriores al cobro exitoso
5. Si el pago falla, el proceso de reintentos de Stripe aplica automáticamente

## Endpoints
- `POST /api/v1/webhooks/stripe` — Recibir invoice.payment_succeeded e invoice.payment_failed
- `GET /api/v1/invoices` — Listar invoices del tenant
- `GET /api/v1/invoices/{invoice_id}` — Descargar invoice PDF

## Health Check
- `GET /health` → { "status": "ok" }