# SPEC-07-042 — Reintentos de Pago Fallido (3 Intentos en 7 Días)

## Metadata
- **RF origen**: RF-042
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, stripe-integration, notification-service

---

## User Story
**Como** administrador de ParkCore **quiero** que los pagos fallidos se reintenten automáticamente antes de suspender al tenant **para** dar oportunidad de resolver problemas de pago sin interrumpir el servicio prematuramente.

## Objetivo
El sistema debe confiar en los reintentos automáticos de Stripe para pagos fallidos de renovación de suscripción, con un máximo de 3 intentos en un periodo de 7 días, antes de proceder con la suspensión.

## Comportamiento Específico

### Happy Path
1. Día 0: Primer intento de cobro (renovación). Si falla: Stripe programa reintento a las 24h
2. Día 1: Segundo intento. Si falla: Stripe envía webhook invoice.payment_failed
3. Sistema registra evento y envía email con enlace al Stripe Customer Portal
4. Día 2: Tercer intento. Si falla: se programa último reintento en 48h
5. Día 4: Último intento. Si falla: Stripe marca suscripción como unpaid
6. Sistema recibe webhook; detecta que es el intento final; inicia flujo de suspensión

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tenant actualiza método de pago antes del tercer intento | El siguiente cobro usa el nuevo método |
| Método de pago removido completamente | Stripe no puede reintentar; suspensión inmediata |
| Tarjeta reportada como perdida o robada | Stripe no reintenta; suspensión inmediata |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| stripe_invoice_id | string | ID de la invoice de Stripe | Sí |
| tenant_id | UUID | Tenant asociado | Sí |
| attempt_count | integer | Número de intento (1, 2, 3) | Sí |
| failure_code | string | Código de error de Stripe | Sí |
| failure_message | string | Mensaje descriptivo del error | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| subscription_status | enum | active, past_due, unpaid |
| attempts_made | integer | Número de intentos realizados |
| next_attempt_at | datetime | Fecha del próximo intento |
| days_until_suspension | integer | Días restantes hasta suspensión |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Los reintentos se ejecutan en los días 1, 2 y 4 (24h, 48h, 96h desde el intento inicial)
2. Cada intento fallido genera un email de notificación al tenant admin
3. Cada intento fallido genera un evento payment_failed en la tabla de eventos SaaS
4. El email incluye siempre el enlace directo al Stripe Customer Portal
5. Si después de 3 intentos no hay pago exitoso, el sistema inicia la suspensión del tenant

## Endpoints
- `POST /api/v1/webhooks/stripe` — Recibir invoice.payment_failed

## Health Check
- `GET /health` → { "status": "ok" }