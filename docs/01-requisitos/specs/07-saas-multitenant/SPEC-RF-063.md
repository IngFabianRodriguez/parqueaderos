# SPEC-07-saas-multitenant-063 — El sistema debe calcular y almacenar el MRR (Monthly Recurring Revenue) de ca...

## Metadata
- **RF origen**: RF-063
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de ParkCore **quiero** conocer el MRR (Monthly Recurring Revenue) de cada tenant mes a mes **para** entender la salud del negocio, hacer proyecciones y tomar decisiones basadas en datos. ---

## Objetivo
El sistema debe calcular y almacenar el MRR (Monthly Recurring Revenue) de cada tenant activo al final de cada mes, considerando el plan_base del tenant + overage_billing - descuentos. EI MRR se desglosa por plan y se almacena para construir la curva de crecimiento y análisis de tendencias. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | tenant_id | UUID | Tenant | | month | string | Mes en formato YYYY-MM | | plan_mrr | decimal | MRR base del plan | | overage_mrr | decimal | MRR por excedentes | | discounts_mrr | decimal | Descuentos recurrentes | | total_mrr | decimal | MRR total (plan + overage - discounts) | | calculated_at | datetime | Timestamp del cálculo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | tenant_id | UUID | Tenant | | month | string | Mes en formato YYYY-MM | | plan_mrr | decimal | MRR base del plan | | overage_mrr | decimal | MRR por excedentes | | discounts_mrr | decimal | Descuentos recurrentes | | total_mrr | decimal | MRR total (plan + overage - discounts) | | calculated_at | datetime | Timestamp del cálculo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El MRR se calcula diariamente para el mes en curso y se almacena en `mrr_history`. 2. El MRR final de un mes cerrado es inmutable y se genera el primer día del mes siguiente. 3. El MRR se desglosa en: `plan_mrr`, `overage_mrr`, `discounts_mrr`, `total_mrr`. 4. El MRR de planes annual se convierte a monthly equivalent (precio / 12). 5. Los one-time charges (prorrateos, upgrades únicos) no se incluyen en el MRR recurrente. 6. El MRR total de la plataforma se puede consultar por: mes, plan, segmento de tenants. 7. Los eventos `mrr_calculated` se generan diariamente para tracking en tiempo real. ---

## Endpoints
- `GET /api/v1/metrics/mrr` — Consultar MRR de la plataforma - `GET /api/v1/metrics/mrr?tenant_id={id}` — Consultar MRR de un tenant específico - `GET /api/v1/metrics/mrr/historical?from=YYYY-MM&to=YYYY-MM` — MRR histórico ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El MRR es la métrica fundamental del negocio SaaS; se debe calcular con precisión y auditoria. - Los descuentos recurring incluyen: descuentos por pago annual anticipado, descuentos por volumen, coupons recurrentes. - Los descuentos one-time ( coupon de bienvenida, descuento de prueba) no afectan el MRR. - El MRR se usa para calcular el ARR (Annual Recurring Revenue) = MRR * 12.
