# SPEC-07-saas-multitenant-065 — El sistema debe calcular el Net Revenue Retention (NRR) mensual, que mide el ...

## Metadata
- **RF origen**: RF-065
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de ParkCore **quiero** conocer el NRR (Net Revenue Retention) mensual **para** saber cuánto revenue estamos generando de los tenants que teníamos el mes pasado, considerando expansiones, contracciones y churn. ---

## Objetivo
El sistema debe calcular el Net Revenue Retention (NRR) mensual, que mide el revenue real generado por los tenants activos al inicio del mes, incluyendo: renovación del MRR base, revenue de upgrades (expansión), revenue perdido por downgrades (contracción), y revenue perdido por churn. Un NRR > 100% indica que el revenue está creciendo incluso sin nuevos tenants. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | month | string | Mes calculado | | starting_mrr | decimal | MRR al inicio del mes | | renewal_mrr | decimal | MRR renovado sin cambios | | expansion_mrr | decimal | MRR ganado por upgrades | | contraction_mrr | decimal | MRR perdido por downgrades | | churned_mrr | decimal | MRR perdido por churn | | new_mrr | decimal | MRR de nuevos tenants (no cuenta en NRR base) | | nrr | decimal | Net Revenue Retention (%) | | calculated_at | datetime | Timestamp del cálculo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | month | string | Mes calculado | | starting_mrr | decimal | MRR al inicio del mes | | renewal_mrr | decimal | MRR renovado sin cambios | | expansion_mrr | decimal | MRR ganado por upgrades | | contraction_mrr | decimal | MRR perdido por downgrades | | churned_mrr | decimal | MRR perdido por churn | | new_mrr | decimal | MRR de nuevos tenants (no cuenta en NRR base) | | nrr | decimal | Net Revenue Retention (%) | | calculated_at | datetime | Timestamp del cálculo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El NRR se calcula mensualmente y se almacena en `nrr_metrics`. 2. La fórmula considera: Starting MRR, Expansion, Contraction, y Churned MRR. 3. El NRR > 100% indica crecimiento de revenue sin nuevos tenants. 4. El NRR se desglosa por plan para ver cuál segmento está expansándose más. 5. Se genera alerta si NRR > 130% o NRR < 85%. 6. Los nuevos tenants no se incluyen en el cálculo del NRR base (son \"新增\"). 7. El evento `nrr_calculated` se genera después de cada cálculo. ---

## Endpoints
- `GET /api/v1/metrics/nrr` — Consultar NRR actual y histórico - `GET /api/v1/metrics/nrr?month=YYYY-MM` — NRR de un mes específico - `GET /api/v1/metrics/nrr/by-plan` — NRR desglosado por plan ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El NRR es la métrica más importante de un negocio SaaS porque muestra si el negocio está realmente creciendo con la base de clientes existente. - Un NRR de 110% significa que por cada $100 que teníamos hace un mes, ahora tenemos $110 (sin contar nuevos tenants). - Los nuevos tenants sí contribuyen al revenue total pero no al NRR; el NRR solo mide retención y expansión de la base existente. - El NRR se puede segmentar por: plan, antigüedad del tenant, sector, tamaño. - El NRR se correlaciona con el Churn Rate: alto churn baja el NRR, bajo churn y alta expansión lo sube.
