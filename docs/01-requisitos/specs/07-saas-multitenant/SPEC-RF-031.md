# SPEC-07-031 — Periodo de Trial de 14 Días Sin Cobro

## Metadata
- **RF origen**: RF-031
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: tenant-service, billing-service, notification-service

---

## User Story
**Como** nuevo cliente de ParkCore **quiero** probar la plataforma durante 14 días sin costo **para** evaluar si se ajusta a mis necesidades antes de comprometerme con un pago.

## Objetivo
Todo nuevo tenant creado debe iniciar automáticamente en un periodo de prueba de 14 días durante el cual no se genera ningún cargo, no se requiere información de pago por adelantado, y el acceso a las funcionalidades está sujeto únicamente a los límites del plan Starter trial.

## Comportamiento Específico

### Happy Path
1. Al crearse el tenant (RF-029), sistema asigna trial_start_date = NOW() y trial_end_date = NOW() + 14 días
2. Sistema muestra en dashboard: "Tienes X días restantes de tu periodo de prueba"
3. Al día 7: sistema envía email recordatorio
4. Al día 12: sistema envía email "Quedan 2 días"
5. Al día 14 sin suscripción: estado cambia a trial_expired o canceled según uso

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Trial expira con transacciones | Cambiar a trial_expired; acceso read-only |
| Trial expira sin transacciones | Marcar como canceled; comenzar retención de 90 días |
| Pago falla durante conversión | Mantener trial hasta que se resuelva |
| Tenant hace upgrade antes del día 14 | Conversión inmediata; sin prorrateo |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| plan_seleccionado | string | Plan elegido al hacer upgrade | Sí (al suscribir) |
| stripe_customer_id | string | ID del cliente en Stripe | Sí (al suscribir) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| status | enum | trial, trial_expired, active, canceled |
| trial_start_date | datetime | Fecha de inicio del trial |
| trial_end_date | datetime | Fecha de fin del trial |
| trial_converted_at | datetime | Fecha de conversión (null si no se ha convertido) |
| days_remaining | integer | Días restantes del trial |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo tenant nuevo inicia con status = trial y trial_end_date = fecha actual + 14 días
2. Ningún cargo se genera automáticamente durante los 14 días de trial
3. El banner "X días restantes de tu trial" es visible en el dashboard
4. Se envía email recordatorio al día 7 y al día 12
5. Al día 15, si no hay suscripción activa, el estado cambia a trial_expired o canceled
6. En trial_expired, el tenant puede ver sus datos pero no registrar nuevas transacciones
7. La conversión a active ocurre exactamente cuando el primer pago se confirma

## Endpoints
- `POST /api/v1/subscriptions` — Crear suscripción (upgrade durante trial o después)
- `GET /api/v1/tenants/{tenant_id}/status` — Consultar estado y días restantes
- `POST /api/v1/webhooks/stripe` — Confirmar pago y disparar conversión

## Health Check
- `GET /health` → { "status": "ok" }