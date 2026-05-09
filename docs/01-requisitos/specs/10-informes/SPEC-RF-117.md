# SPEC-10-informes-117 — El sistema debe permitir que todo reporte del módulo de Informes sea filtrabl...

## Metadata
- **RF origen**: RF-117
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin o sede_admin **quiero** aplicar múltiples filtros a cualquier reporte **para** obtener datos específicos según la sede, operador, cliente, rango de fechas o tipo de vehículo que me interese analizar. ---

## Objetivo
El sistema debe permitir que todo reporte del módulo de Informes sea filtrable por uno o más de los siguientes criterios: sede, operador, cliente, rango de fechas y tipo de vehículo. Los filtros son combinables entre sí y se aplican antes de cualquier agregación o cálculo. ---

## Comportamiento Específico

### Happy Path
1. El usuario construye la consulta de reporte añadiendo uno o más parámetros de filtro 2. El `reporting-service` valida cada filtro: a. Verifica que el `sede_id` exista y que el usuario tenga acceso b. Verifica que el `operador_id` exista y pertenezca a una sede accesible c. Verifica que el `cliente_id` exista d. Verifica que `tipo_vehiculo` sea un valor válido del catálogo e. Verifica que `fecha_inicio <= fecha_fin` 3. Se construye la consulta con los filtros activos aplicados en la capa de datos 4. Se ejecuta la consulta y se retorna el resultado 5. La respuesta incluye los filtros aplicados y advertencias si algunos fueron ignorados ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | filtros_aplicados | object | Objeto con cada filtro y su valor | | advertencias | array | Lista de advertencias (ej: filtro ignorado por no existir) | | datos | object | Resultado del reporte con los filtros aplicados | | total_registros | integer | Cantidad de registros que cumplen los filtros | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | filtros_aplicados | object | Objeto con cada filtro y su valor | | advertencias | array | Lista de advertencias (ej: filtro ignorado por no existir) | | datos | object | Resultado del reporte con los filtros aplicados | | total_registros | integer | Cantidad de registros que cumplen los filtros | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Cualquier combinación de filtros válidos debe retornar el subconjunto de datos correspondiente 2. Los filtros no aplicados (nulos o vacíos) no deben afectar el resultado 3. Un filtro por operador que no existe no debe causar error, sino warn + ignore 4. El tiempo de respuesta con 5 filtros activos debe ser < 3 segundos para 1 año de datos 5. La respuesta siempre incluye `filtros_aplicados` mostrando qué filtros se usaron ---

## Endpoints
- `GET /api/v1/reports/income` — Recibe filtros como query params - `GET /api/v1/reports/occupancy` — Recibe filtros como query params - `GET /api/v1/reports/{report_type}` — Endpoint genérico de reportes con filtros ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Este RF define la interfaz de filtrado que todos los demás reportes del módulo heredan - Los filtros deben documentarse en el OpenAPI del servicio de reporting - Se recomienda cachear resultados de filtros frecuentes para mejorar rendimiento
