# SPEC-07-032 — Conversión de Trial a Suscripción Activa

## Metadata
- **RF origen**: RF-032
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, tenant-service, notification-service

---

## User Story
**Como** usuario de un tenant en trial **quiero** que mi cuenta se convierta automáticamente a suscripción activa cuando realice mi primer pago **para** que mi acceso a la plataforma sea permanente y no haya interrupciones.

## Objetivo
El sistema debe detectar el primer pago exitoso de un tenant en estado trial y convertir su estado a active, registrando la suscripción en Stripe, actualizando el plan asociado y generando el evento de métricas correspondiente.

## Comportamiento Específico

### Happy Path
1. Tenant inicia flujo de upgrade desde dashboard
2. Sistema crea o reutiliza Stripe Customer para el tenant
3. Sistema crea Stripe Subscription con el plan seleccionado
4. Usuario completa el pago en Stripe
5. Stripe envía webhook invoice.payment_succeeded
6. Sistema verifica tenant tiene estado trial
7. Sistema actualiza estado del tenant a active
8. Sistema crea registro de subscription
9. Sistema genera evento trial_converted
10. Sistema envía email de confirmación

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Pago exitoso pero webhook llega duplicado | Verifica si ya se hizo la conversión; si ya está active, no hacer nada (idempotencia) |
| Pago exitoso pero tenant ya está active | Ignorar conversión; suscripción se actualiza como renovación normal |
| Pago fallido | Mantener en trial; Stripe maneja reintentos |
| Trial ya expiró y se convierte | trial_end_date queda como converted_at |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| plan | enum | Plan seleccionado (starter, professional, enterprise, custom) | Sí |
| stripe_customer_id | string | ID del cliente en Stripe | Sí |
| billing_cycle | enum | Ciclo de facturación (monthly, annual) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| tenant_id | UUID | Tenant convertido |
| status | enum | active |
| subscription_id | UUID | ID interno de la suscripción |
| stripe_subscription_id | string | ID de la suscripción en Stripe |
| plan | string | Plan activado |
| current_period_start | datetime | Inicio del periodo |
| current_period_end | datetime | Fin del periodo |
| converted_at | datetime | Timestamp de conversión |
| mrr | decimal | MRR del tenant |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un pago exitoso en Stripe para un tenant en trial convierte automáticamente a active
2. La conversión ocurre en menos de 5 segundos después de recibir el webhook
3. El registro de subscription contiene el stripe_subscription_id vinculado al tenant
4. El evento trial_converted se genera con tenant_id, plan, converted_at, mrr
5. El MRR del tenant se actualiza en mrr_history el mismo día de la conversión

## Endpoints
- `POST /api/v1/subscriptions/create-checkout` — Crear Stripe Checkout session
- `POST /api/v1/webhooks/stripe` — Recibir webhooks de Stripe
- `GET /api/v1/tenants/{tenant_id}/subscription` — Consultar estado de suscripción

## Health Check
- `GET /health` → { "status": "ok" }