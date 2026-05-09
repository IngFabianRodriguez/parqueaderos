# SPEC-07-045 — Escucha de Webhooks de Stripe para Pagos, Cambios de Plan y Cancelaciones

## Metadata
- **RF origen**: RF-045
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, webhook-service, tenant-service

---

## User Story
**Como** sistema de ParkCore **quiero** escuchar los webhooks de Stripe para enterarme en tiempo real de pagos, cambios de plan y cancelaciones **para** mantener el estado de los tenants sincronizado con Stripe.

## Objetivo
El sistema debe exponer un endpoint único de webhooks que Stripe llamará cada vez que ocurra un evento relevante (pago exitoso, pago fallido, cambio de plan, cancelación). El endpoint debe verificar la firma de cada request, procesar el evento idempotentemente, y actualizar el estado del tenant correspondientemente.

## Comportamiento Específico

### Flujo de Recepción de Webhooks
1. Stripe envía `POST /api/v1/webhooks/stripe` con cuerpo JSON y headers (`stripe-signature`)
2. El middleware extrae el body raw y el header `stripe-signature`
3. Verifica la firma usando `stripe.webhooks.constructEvent()` con el secret `STRIPE_WEBHOOK_SECRET`
4. Si la firma es inválida: retorna 401 Unauthorized
5. Parsea el cuerpo, extrae `type` (nombre del evento) y `data.object` (el objeto afectado)
6. Busca el handler correspondiente y lo ejecuta
7. Retorna HTTP 200 con `{ received: true }`

### Handlers por Tipo de Evento
| Evento | Acción |
|---------|--------|
| `checkout.session.completed` | Crear/finalizar suscripción del tenant (RF-032) |
| `invoice.payment_succeeded` | Marcar invoice como `paid` (RF-043); actualizar `current_period_end` |
| `invoice.payment_failed` | Registrar intento en `payment_attempts` (RF-042); si `attempt_count = 3`, iniciar suspensión (RF-035) |
| `customer.subscription.updated` | Actualizar `plan_id` en `subscriptions` (upgrade/downgrade) |
| `customer.subscription.deleted` | Marcar tenant como `canceled` (RF-036) |
| `invoice.created` | Registrar (no actualizar estado del tenant) |
| `payment_method.attached` | Actualizar `default_payment_method_id` en `tenants` |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Firma de webhook inválida | Retornar 401; no procesar; loguear como intento de fraude |
| Webhook duplicado (mismo event_id) | Si ya se procesó, retornar 200 sin hacer nada (idempotencia) |
| Evento de un tenant que ya no existe | Ignorar el evento; loguear warning |
| Tipo de evento no reconocido | Loguear como `unknown_event_type`; retornar 200 (no bloquear a Stripe) |
| El handler lanza exception | Retornar 500; Stripe reintenta hasta 24h |
| La DB está caída | Retornar 503; Stripe reintenta con backoff |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| stripe-signature | string | Firma de verificación del webhook | Sí |
| event_type | string | Tipo de evento de Stripe | Sí |
| event_id | string | ID único del evento (para idempotencia) | Sí |
| customer_id | string | Stripe Customer ID | Sí |
| subscription_id | string | Stripe Subscription ID | Sí |
| invoice_id | string | Stripe Invoice ID | Sí (invoice events) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| processed | boolean | Si el evento fue procesado exitosamente |
| event_id | string | ID del evento de Stripe (para logging) |
| action_taken | string | Descripción de la acción tomada |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El endpoint de webhooks procesa todos los eventos de Stripe listados en el flujo funcional
2. La verificación de firma ocurre antes de cualquier procesamiento; eventos con firma inválida se rechazan con 401
3. Cada evento se procesa idempotentemente (el mismo evento enviado dos veces produce el mismo resultado)
4. El `event_id` de cada webhook recibido se registra en `webhook_events` para evitar duplicados
5. Los eventos desconocidos se loguean pero no fallan el endpoint (retorna 200)
6. El tiempo de procesamiento de cada webhook < 2 segundos

## Endpoints
- `POST /api/v1/webhooks/stripe` — Endpoint único de webhooks de Stripe

## Health Check
- `GET /health` → { "status": "ok" }