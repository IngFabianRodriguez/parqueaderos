# SPEC-10-informes-119 — El sistema debe generar un reporte que muestre, para cada hora del día (0-23)...

## Metadata
- **RF origen**: RF-119
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sede_admin o tenant_admin **quiero** consultar la ocupación de mi sede por hora **para** saber en qué horarios hay más espacios ocupados, cuál es la tasa de ocupación y cuál es la duración promedio de cada vehículo en el parqueadero. ---

## Objetivo
El sistema debe generar un reporte que muestre, para cada hora del día (0-23) dentro del rango de fechas seleccionado, la cantidad de espacios ocupados, la tasa de ocupación como porcentaje (ocupados / total espacios) y la duración promedio de las transacciones que estuvieron activas en esa hora. ---

## Comportamiento Específico

### Happy Path
1. El usuario solicita el reporte de ocupación con filtros (RF-117): sede, rango de fechas 2. El `reporting-service` obtiene la configuración de la sede: `total_espacios` 3. Para cada hora h (0 a 23) dentro del rango de fechas: a. Cuenta transacciones activas (status `open` o `closed` con `hora_entrada <= h < hora_salida`) b. Calcula `tasa_ocupacion = (ocupados / total_espacios) * 100` c. Calcula `duracion_promedio` de las transacciones que cerraron en esa hora 4. Agrega los promedios generales del período 5. Si `include_comparison=true`, aplica la lógica de RF-118 (comparativa con período anterior) 6. Retorna el reporte horario ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | total_espacios | integer | Capacidad total de la sede | | datos_por_hora | array | Array de 24 objetos (uno por hora) | | datos_por_hora[].hora | integer | Hora del día (0-23) | | datos_por_hora[].espacios_ocupados | integer | Cantidad de espacios con vehículo activo | | datos_por_hora[].tasa_ocupacion_porcentual | decimal | Porcentaje (0.00 - 100.00) | | datos_por_hora[].duracion_promedio_minutos | decimal | Duración promedio en minutos de transacciones cerradas | | datos_por_hora[].transacciones_cerradas | integer | Cantidad de transacciones que cerraron en esa hora | | resumen | object | Promedio de todos los indicadores en el período | | resumen.tasa_ocupacion_promedio | decimal | Promedio de tasa de ocupación en el período | | resumen.duracion_promedio_general | decimal | Duración promedio general del período | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | total_espacios | integer | Capacidad total de la sede | | datos_por_hora | array | Array de 24 objetos (uno por hora) | | datos_por_hora[].hora | integer | Hora del día (0-23) | | datos_por_hora[].espacios_ocupados | integer | Cantidad de espacios con vehículo activo | | datos_por_hora[].tasa_ocupacion_porcentual | decimal | Porcentaje (0.00 - 100.00) | | datos_por_hora[].duracion_promedio_minutos | decimal | Duración promedio en minutos de transacciones cerradas | | datos_por_hora[].transacciones_cerradas | integer | Cantidad de transacciones que cerraron en esa hora | | resumen | object | Promedio de todos los indicadores en el período | | resumen.tasa_ocupacion_promedio | decimal | Promedio de tasa de ocupación en el período | | resumen.duracion_promedio_general | decimal | Duración promedio general del período | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La suma de `espacios_ocupados` a lo largo de las 24 horas puede superar el total de transacciones (una transacción cuenta en múltiples horas) 2. `tasa_ocupacion` se calcula como `(ocupados / total_espacios) * 100` con 2 decimales 3. `duracion_promedio` se calcula solo con transacciones `closed` que cerraron en esa hora 4. Si `include_comparison=true`, se añade la comparativa RF-118 para cada hora 5. El reporte se genera en menos de 10 segundos para un año de datos ---

## Endpoints
- `GET /api/v1/reports/occupancy/hourly` — Reporte de ocupación por hora - `GET /api/v1/sedes/{sede_id}/config` — Consulta de `total_espacios` ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Si existe un `occupancy_log` que registre ocupación por minuto, se usa ese para mayor precisión; si no, se calcula a partir de `transactions` - La `tasa_ocupacion` puede superar el 100% si hay sobrecupo (más vehículos que espacios reportados) - Para rangos mayores a 1 mes, se recomienda que la UI agrupe por día y muestre un promedio por hora - Este reporte es la base para el heatmap de RF-120
