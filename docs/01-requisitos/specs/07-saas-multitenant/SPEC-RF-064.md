# SPEC-07-saas-multitenant-064 — El sistema debe calcular el Churn Rate mensual como el porcentaje de tenants ...

## Metadata
- **RF origen**: RF-064
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de ParkCore **quiero** conocer el Churn Rate mensual **para** saber cuántos clientes perdimos en el mes y tomar acciones para reducir la fuga. ---

## Objetivo
El sistema debe calcular el Churn Rate mensual como el porcentaje de tenants que cambiaron a estado `churned` o `canceled` durante el mes respecto al total de tenants activos al inicio del mes. El resultado se desglosa por plan, segmento y motivo de churn. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | month | string | Mes calculado | | total_tenants_start | integer | Tenants activos al inicio del mes | | churned_tenants | integer | Tenants perdidos durante el mes | | churn_rate | decimal | Porcentaje de churn (0.05 = 5%) | | revenue_churn_rate | decimal | Porcentaje de MRR perdido | | by_plan | object | Churn rate por plan | | by_reason | object | Desglose por motivo de churn | | calculated_at | datetime | Timestamp del cálculo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | month | string | Mes calculado | | total_tenants_start | integer | Tenants activos al inicio del mes | | churned_tenants | integer | Tenants perdidos durante el mes | | churn_rate | decimal | Porcentaje de churn (0.05 = 5%) | | revenue_churn_rate | decimal | Porcentaje de MRR perdido | | by_plan | object | Churn rate por plan | | by_reason | object | Desglose por motivo de churn | | calculated_at | datetime | Timestamp del cálculo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El Churn Rate se calcula mensualmente y se almacena en `churn_metrics`. 2. El cálculo usa: tenants activos al inicio del mes / tenants que hicieron churn durante el mes. 3. Se desglosa por plan, segmento y motivo de churn. 4. El MRR perdido por churn se calcula y almacena como `revenue_churn_rate`. 5. Se genera alerta cuando el churn rate mensual excede el threshold configurable (default 5%). 6. Los datos históricos de churn rate están disponibles para comparar mes a mes. 7. El evento `churn_calculated` se genera después de cada cálculo. ---

## Endpoints
- `GET /api/v1/metrics/churn` — Consultar churn rate actual y histórico - `GET /api/v1/metrics/churn?month=YYYY-MM` — Churn rate de un mes específico ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El churn rate es una de las métricas más importantes del negocio SaaS; se monitorea semanalmente en las reviews de leadership. - Un churn rate alto puede indicar problemas con el producto, pricing, o servicio al cliente. - El "churn preventable" (cancelaciones por falta de pago donde se podría haber retenido) se mide para evaluar efectividad de estrategias de retención.
