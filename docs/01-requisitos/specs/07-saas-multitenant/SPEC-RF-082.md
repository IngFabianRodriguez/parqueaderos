# SPEC-07-saas-multitenant-082 — El sistema debe proporcionar al admin de la empresa B2B (`company_admin`) un ...

## Metadata
- **RF origen**: RF-082
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de una empresa B2B con flota de vehículos **quiero** acceder a reportes que muestren el uso que mis vehículos hacen de los estacionamientos **para** controlar gastos, verificarUsage y tomar decisiones sobre asignaciones de vehículos. ---

## Objetivo
El sistema debe proporcionar al admin de la empresa B2B (`company_admin`) un portal con reportes de uso de su flota. Los reportes incluyen: uso por vehículo (transacciones, tiempo, monto), uso por sede del tenant, tendencias mensuales, сравнение entre vehículos, y alertas de límite de gasto. Estos reportes permiten a la empresa gestionar suflota sin depender del tenant. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
### Resumen ejecutivo (dashboard) | Campo | Tipo | Descripción | |-------|------|-------------| | active_vehicles_count | integer | Número de vehículos con al menos 1 transacción en el mes | | current_month_spend | decimal | Gasto total del mes actual | | current_month_limit | decimal | Límite total de la flota (suma de límites vehiculares o default) | | spend_percentage | float | Porcentaje del gasto vs límite total | | near_limit_vehicles | array | Lista de vehículos con > 80% del límite usado | | over_limit_vehicles | array | Lista de vehículos que excedieron el límite | | last_3_months_trend | array | Gasto mensual de los últimos 3 meses { month, amount } | ### Reporte de uso por vehículo | Campo | Tipo | Descripción | |-------|------|-------------| | vehicle_id | uuid | ID del vehículo | | license_plate | string | Matrícula | | description | string | Descripción del vehículo | | transaction_count | integer | Número de transacciones | | total_time_minutes | integer | Tiempo total de estacionamiento | | total_amount | decimal | Monto total facturado | | limit_used_percentage | float | Porcentaje del límite de gasto usado | | status | enum | `normal`, `near_limit`, `over_limit` | ---

## Datos de Salida
### Resumen ejecutivo (dashboard) | Campo | Tipo | Descripción | |-------|------|-------------| | active_vehicles_count | integer | Número de vehículos con al menos 1 transacción en el mes | | current_month_spend | decimal | Gasto total del mes actual | | current_month_limit | decimal | Límite total de la flota (suma de límites vehiculares o default) | | spend_percentage | float | Porcentaje del gasto vs límite total | | near_limit_vehicles | array | Lista de vehículos con > 80% del límite usado | | over_limit_vehicles | array | Lista de vehículos que excedieron el límite | | last_3_months_trend | array | Gasto mensual de los últimos 3 meses { month, amount } | ### Reporte de uso por vehículo | Campo | Tipo | Descripción | |-------|------|-------------| | vehicle_id | uuid | ID del vehículo | | license_plate | string | Matrícula | | description | string | Descripción del vehículo | | transaction_count | integer | Número de transacciones | | total_time_minutes | integer | Tiempo total de estacionamiento | | total_amount | decimal | Monto total facturado | | limit_used_percentage | float | Porcentaje del límite de gasto usado | | status | enum | `normal`, `near_limit`, `over_limit` | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `company_admin` puede ver reportes de uso de su flota con datos de los últimos 12 meses. 2. Los reportes muestran datos por vehículo y por sede. 3. El dashboard muestra alertas cuando vehículos exceden el 80% del límite de gasto. 4. El `company_admin` puede exportar reportes a CSV y PDF. 5. Los datos están limitados exclusivamente a la flota de la empresa; el `company_admin` no ve datos de otras empresas B2B ni de otros tenants. 6. El `tenant_admin` puede ver los mismos reportes de cualquier empresa de su tenant. 7. Los reportes se actualizan con latencia de hasta 1 hora (no en tiempo real). 8. Las transacciones muestran fecha, hora, sede, duración y monto. ---

## Endpoints
- `GET /api/v1/company/dashboard/summary` — Resumen ejecutivo de la flota - `GET /api/v1/company/reports/usage-by-vehicle` — Reporte de uso por vehículo - `GET /api/v1/company/reports/usage-by-site` — Reporte de uso por sede - `GET /api/v1/company/reports/spending-trend` — Tendencia de gasto mensual - `GET /api/v1/company/vehicles/{vehicle_id}/transactions` — Detalle de transacciones de un vehículo - `GET /api/v1/company/reports/export` — Exportar reporte (query param: `format=csv|pdf`) - `GET /api/v1/tenants/{tenant_id}/companies/{company_id}/reports/*` — Endpoints equivalentes para tenant_admin ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El portal de la empresa B2B es una SPA separada del admin panel del tenant (`/company/*`). - Los reportes de la empresa B2B usan los mismos datos y servicios de analytics que el dashboard BI del tenant (RF-075), pero filtrados por `company_id`. - Se recomienda implementar un dashboard con gráficos de tendencia de gasto por mes para los últimos 6 meses. - La exportación a PDF debe incluir el logo de la empresa si está configurado, además de los datos del reporte.
