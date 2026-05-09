# SPEC-09-observabilidad-113 — El sistema debe permitir buscar logs por `trace_id` para reconstruir el flujo...

## Metadata
- **RF origen**: RF-113
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** equipo de operaciones **quiero** poder buscar todos los logs relacionados con un `trace_id` específico **para** reconstruir el flujo completo de una transacción y diagnosticar problemas de manera rápida. ---

## Objetivo
El sistema debe permitir buscar logs por `trace_id` para reconstruir el flujo completo de una transacción. Todos los logs generados durante el procesamiento de un request compartirán el mismo `trace_id`, permitiendo visualizarlos en orden cronológico y entender exactamente qué pasó en cada microservicio. ---

## Comportamiento Específico

### Happy Path
1. El usuario (operador/admin) ingresa un `trace_id` en el campo de búsqueda del dashboard de logs 2. El `logging-service` recibe la consulta `GET /api/v1/logs?trace_id={trace_id}` 3. El servicio busca en el índice todos los documentos donde `trace_id` = valor ingresado 4. Los resultados se ordenan por timestamp ascendente (cronológico) 5. Se retorna una lista con cada entrada de log incluyendo: servicio, timestamp, acción, mensaje, metadata 6. El dashboard muestra la traza completa como una lista expandible o como un diagrama de flujo 7. Cada entrada de log tiene un link para ver el detalle (span completo) ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | trace_id | UUID v4 | Identificador del trace | | total_logs | integer | Número total de entradas encontradas | | logs | array | Lista de entradas de log ordenadas cronológicamente | | duration_ms | integer | Duración total del trace (primer log a último) | Cada entrada de log: | Campo | Tipo | Descripción | |-------|------|-------------| | timestamp | ISO8601 | Momento en que se generó el log | | service | string | Nombre del microservicio que generó el log | | span_id | UUID | Identificador del span dentro del trace | | level | enum | Nivel: DEBUG, INFO, WARN, ERROR | | action | string | Acción/evento que se registra | | message | string | Mensaje descriptivo del log | | metadata | JSON | Datos adicionales relevantes (user_id, device_id, etc.) | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | trace_id | UUID v4 | Identificador del trace | | total_logs | integer | Número total de entradas encontradas | | logs | array | Lista de entradas de log ordenadas cronológicamente | | duration_ms | integer | Duración total del trace (primer log a último) | Cada entrada de log: | Campo | Tipo | Descripción | |-------|------|-------------| | timestamp | ISO8601 | Momento en que se generó el log | | service | string | Nombre del microservicio que generó el log | | span_id | UUID | Identificador del span dentro del trace | | level | enum | Nivel: DEBUG, INFO, WARN, ERROR | | action | string | Acción/evento que se registra | | message | string | Mensaje descriptivo del log | | metadata | JSON | Datos adicionales relevantes (user_id, device_id, etc.) | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Se puede buscar logs por cualquier `trace_id` generado por el API Gateway 2. Los resultados se muestran en orden cronológico (ascendente por timestamp) 3. Cada resultado incluye: servicio, timestamp, acción, mensaje, span_id 4. La búsqueda responde en menos de 3 segundos para traces de hasta 1000 entradas 5. Se puede filtrar por servicio, nivel de log y rango de fechas 6. Los logs de todos los microservicios están centralizados y consultables ---

## Endpoints
- `GET /api/v1/logs` — Búsqueda de logs con filtros (trace_id, servicio, nivel, rango) - `GET /api/v1/traces/{trace_id}` — Endpoint dedicado para consultar un trace completo - `GET /api/v1/logs/{log_id}` — Detalle de una entrada de log específica ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda usar Elasticsearch o similar para el indexado y búsqueda eficiente de logs - El campo `trace_id` debe ser indexado como keyword para búsquedas exactas rápidas - Para mejorar la experiencia, el dashboard puede mostrar los logs como un "timeline" visual donde cada servicio es una fila - Las métricas de uso del dashboard de logs pueden ayudar a identificar patrones de errores frecuentes
