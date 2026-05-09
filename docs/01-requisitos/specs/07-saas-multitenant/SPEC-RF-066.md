# SPEC-07-saas-multitenant-066 — El sistema debe registrar en la tabla `subscription_events` cada evento relev...

## Metadata
- **RF origen**: RF-066
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sistema de ParkCore **quiero** trackear eventos significativos de suscripción **para** calcular métricas SaaS como MRR, Churn Rate y NRR, y permitir análisis de comportamiento de los tenants a lo largo del tiempo. ---

## Objetivo
El sistema debe registrar en la tabla `subscription_events` cada evento relevante del ciclo de vida de suscripción: `trial_started`, `converted`, `upgraded`, `downgraded`, `churned`, `payment_failed`. Estos eventos alimentan las métricas de negocio y permiten auditoria histórica del comportamiento de cada tenant. ---

## Comportamiento Específico

### Happy Path
1. Un evento ocurre en el sistema de billing o gestión de suscripciones (webhook de Stripe, acción del usuario, cambio de plan). 2. El servicio que procesa la acción (webhook-service, subscription-service) detecta que es un evento trackeable. 3. Se construye el payload del evento: - `event_type`: uno de los tipos definidos. - `tenant_id`: ID del tenant afectado. - `plan_id`: plan vigente después del evento (si aplica). - `previous_plan_id`: plan anterior (para upgrades/downgrades). - `amount`: monto facturado o proyectado (para eventos de revenue). - `metadata`: JSON con datos adicionales específicos del evento. - `occurred_at`: timestamp UTC del evento. 4. Se inserta en `subscription_events`. 5. Se actualiza el estado del tenant según el tipo de evento. 6. Se encola un job para recalcular métricas agregadas. ### Tipos de eventos y su lógica | event_type | Cuándo se dispara | Datos adicionales | |------------|------------------|-------------------| | `trial_started` | Tenant inicia periodo de prueba | `trial_end_date`, `plan_id` | | `converted` | Trial se convierte a subscription paga | `subscription_id`, `plan_id` | | `upgraded` | Plan cambia a uno de mayor precio | `previous_plan_id`, `new_plan_id`, `amount_delta` | | `downgraded` | Plan cambia a uno de menor precio | `previous_plan_id`, `new_plan_id`, `amount_delta` | | `churned` | Suscripción se cancela | `churn_reason`, `cancellation_date` | | `payment_failed` | Pago falla (intento 1, 2 o 3) | `attempt_number`, `invoice_id`, `failure_code` | | `payment_failed_final` | Tercer intento falla y se dispara suspensión | `invoice_id`, `tenant_status` | ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | id | uuid | ID único del evento registrado | | event_type | string | Tipo de evento | | tenant_id | uuid | ID del tenant | | recorded_at | timestamp | Timestamp de registro en el sistema | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | id | uuid | ID único del evento registrado | | event_type | string | Tipo de evento | | tenant_id | uuid | ID del tenant | | recorded_at | timestamp | Timestamp de registro en el sistema | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todos los 7 tipos de eventos (`trial_started`, `converted`, `upgraded`, `downgraded`, `churned`, `payment_failed`, `payment_failed_final`) se registran correctamente en `subscription_events`. 2. Cada registro incluye `tenant_id`, `event_type`, `occurred_at` y `metadata` completa. 3. No hay eventos duplicados para la misma combinación de tenant + evento + timestamp. 4. El registro de eventos no bloquea el flujo principal de suscripción/cancelación. 5. Los eventos están disponibles para consumo por el servicio de métricas (RF-063, RF-064, RF-065). 6. Latencia de inserción < 100ms para el 95% de los casos. ---

## Endpoints
- No expone endpoints REST nuevos; el tracking ocurre internamente via eventos del sistema. - `GET /api/v1/admin/subscription-events` — Consulta de eventos para superadmin (listado paginado, filtrable por tenant, tipo, rango de fechas). ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los eventos son inmutables una vez insertados; no se actualizan ni eliminan. - Se usa una clave única compuesta (`tenant_id`, `event_type`, `occurred_at`) para garantizar idempotencia. - Para debugging, el campo `metadata` puede contener el `event_id` de Stripe cuando el evento proviene de un webhook. - El servicio de analytics consume estos eventos en tiempo real via message queue para actualizar dashboards.
