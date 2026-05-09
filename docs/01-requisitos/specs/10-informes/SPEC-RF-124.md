# SPEC-10-informes-124 — El sistema debe generar un reporte de productividad desglosado por operador, ...

## Metadata
- **RF origen**: RF-124
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de la sede **quiero** consultar el reporte de productividad por operador **para** evaluar el desempeño de cada operario, identificar anomalías y garantizar la correcta gestión de operaciones en la playa. ---

## Objetivo
El sistema debe generar un reporte de productividad desglosado por operador, que incluya el total de transacciones abiertas, transacciones cerradas, cobros realizados, aperturas manuales de talanquera y reembolsos procesdos. El reporte debe ser consultable por rango de fechas y sede. ---

## Comportamiento Específico

### Happy Path
1. El usuario accede al módulo de Reportes y selecciona la categoría "Productividad por Operador". 2. El usuario selecciona la sede (o "Todas las sedes" si tiene permisos multi-sede) y el rango de fechas. 3. El sistema consulta las transacciones, movimientos de talanquera, cobros y reembolsos agrupados por operador. 4. El sistema calcula para cada operador: - Total de transacciones abiertas (estado `OPEN`). - Total de transacciones cerradas (estado `CLOSED`). - Total de cobros realizados (suma de pagos procesados). - Total de aperturas manuales de talanquera (eventos con origen `MANUAL`). - Total de reembolsos procesados (eventos tipo `REFUND`). - Tiempo promedio de operación (diferencia entre primer y último evento del turno). 5. El sistema presenta los resultados en una tabla con columnas ordenables y un resumen consolidado. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | operador_id | UUID | Identificador del operador | | operador_nombre | String | Nombre completo del operador | | transacciones_abiertas | Integer | Cantidad de transacciones en estado OPEN | | transacciones_cerradas | Integer | Cantidad de transacciones en estado CLOSED | | total_cobros | Decimal | Sumatoria de montos cobrados (COP) | | aperturas_manuales | Integer | Cantidad de eventos de apertura manual | | reembolsos | Integer | Cantidad de reembolsos procesados | | monto_reembolsos | Decimal | Sumatoria de montos reembolsados (COP) | | tiempo_promedio_operacion | Integer | Duración promedio en minutos por transacción | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | operador_id | UUID | Identificador del operador | | operador_nombre | String | Nombre completo del operador | | transacciones_abiertas | Integer | Cantidad de transacciones en estado OPEN | | transacciones_cerradas | Integer | Cantidad de transacciones en estado CLOSED | | total_cobros | Decimal | Sumatoria de montos cobrados (COP) | | aperturas_manuales | Integer | Cantidad de eventos de apertura manual | | reembolsos | Integer | Cantidad de reembolsos procesados | | monto_reembolsos | Decimal | Sumatoria de montos reembolsados (COP) | | tiempo_promedio_operacion | Integer | Duración promedio en minutos por transacción | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El reporte muestra exactamente los contadores descritos (transacciones abiertas/cerradas, cobros, aperturas manuales, reembolsos) para cada operador activo en el período. 2. El reporte es filtrable por sede, rango de fechas y operador individual. 3. Los totales del reporte coinciden con la suma de las transacciones individuales que lo componen. 4. El reporte puede exportarse a Excel (.xlsx), CSV y PDF. 5. El tiempo de generación del reporte no excede 5 segundos para un período de 30 días. 6. Si un operador tiene 0 transacciones, sigue apareciendo en el reporte con contadores en cero. ---

## Endpoints
- `GET /api/v1/reports/productivity/operator` — Genera el reporte de productividad por operador - `GET /api/v1/reports/productivity/operator/export` — Exporta el reporte en formato solicitado ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los reembolsos se cuentan de forma separada a los cobros; el monto reembolsado no resta del total de cobros en el resumen. - Las transacciones en estado `VOID` se excluyen del conteo de productividad. - El campo `operador_nombre` se lee de la tabla `operators`; si el operador fue dado de baja, se muestra "Operador inactivo".
