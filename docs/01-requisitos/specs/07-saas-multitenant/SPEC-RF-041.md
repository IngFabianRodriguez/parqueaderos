# SPEC-07-041 — Downgrade de Plan al Final del Ciclo de Facturación

## Metadata
- **RF origen**: RF-041
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, stripe-integration, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** hacer downgrade de mi plan al final de mi ciclo de facturación actual **para** reducir mi costo mensual si ya no necesito las features del plan actual.

## Objetivo
El sistema debe permitir que un tenant solicite un downgrade de plan, programándolo para que se aplique al final del ciclo de facturación actual, sin afectar el servicio durante el periodo restante.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Suscripción > "Hacer downgrade"
2. Sistema muestra los planes disponibles y las features que se perderán
3. Tenant admin selecciona el plan destino y confirma
4. Sistema crea registro en scheduled_plan_changes con effective_date = current_period_end
5. Dashboard muestra banner: "Downgrade programado para el [fecha]"
6. En la fecha de renovación: job aplica el downgrade

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tenant ya tiene downgrade programado | Error "Ya tienes un downgrade programado" |
| Plan destino tiene límites menores que el uso actual | Permitir downgrade; se facturará como overage |
| Tenant cancela el downgrade antes de la fecha | Puede cancelar desde Settings > Suscripción |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| new_plan | enum | Plan destino (debe ser más económico que el actual) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| current_plan | string | Plan actual (hasta la fecha de生效) |
| new_plan | string | Plan que se activará |
| effective_date | datetime | Fecha de生效 del downgrade |
| features_lost | array | Lista de features que se perderán |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un downgrade solicitado se aplica exactamente en current_period_end, no antes
2. El tenant mantiene acceso a todas las features de su plan actual hasta la fecha de生效
3. Se notifica al tenant por email en ambos momentos (solicitud y aplicación)
4. Los feature flags del plan nuevo se activan al inicio del nuevo periodo
5. Solo un downgrade programado por ciclo

## Endpoints
- `POST /api/v1/subscriptions/downgrade` — Programar downgrade
- `DELETE /api/v1/subscriptions/downgrade` — Cancelar downgrade programado
- `GET /api/v1/tenants/{tenant_id}/scheduled-change` — Consultar cambio programado

## Health Check
- `GET /health` → { "status": "ok" }