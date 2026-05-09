# SPEC-09-observabilidad-112 — El sistema debe asignar un `trace_id` (UUID v4) a cada request API entrante e...

## Metadata
- **RF origen**: RF-112
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** equipo de operaciones **quiero** que cada request API tenga un identificador único (trace_id) que se propagué a todos los microservicios involucrados **para** poder reconstruir el flujo completo de una transacción cuando algo falla. ---

## Objetivo
El sistema debe asignar un `trace_id` (UUID v4) a cada request API entrante en el API Gateway. Este `trace_id` debe propagarse a todos los microservicios involucrados mediante headers HTTP (`X-Trace-ID`) y almacenarse en los logs de cada servicio para permitir la correlación posterior. ---

## Comportamiento Específico

### Happy Path
1. Un cliente envía una request HTTP al API Gateway 2. El API Gateway genera un `trace_id` (UUID v4) si no existe en los headers 3. El API Gateway inyecta el header `X-Trace-ID: {trace_id}` en la request 4. El API Gateway registra en su log: `[TRACE] {trace_id} {method} {path} {status} {duration_ms}` 5. El API Gateway reenvía la request al microservicio correspondiente 6. El microservicio recibe la request y lee el header `X-Trace-ID` 7. El microservicio incluye el `trace_id` en todos sus logs: `[TRACE] {trace_id} {service} {action} {details}` 8. Si el microservicio llama a otro servicio (ej: pagos → database), inyecta `X-Trace-ID` en la llamada 9. Todos los spans de un trace comparten el mismo `trace_id` 10. Al completar la request, el trace completo queda disponible para búsqueda ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | trace_id | UUID v4 | Propagado en header X-Trace-ID | | Logs por servicio | JSON | Cada servicio registra sus logs con trace_id | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | trace_id | UUID v4 | Propagado en header X-Trace-ID | | Logs por servicio | JSON | Cada servicio registra sus logs con trace_id | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todo request HTTP que entre al API Gateway recibe un `trace_id` único 2. El `trace_id` está presente en el 100% de los logs generados durante el procesamiento del request 3. El `trace_id` se propaga a todas las llamadas internas entre microservicios 4. Los logs son consultables por `trace_id` en el sistema centralizado de logs 5. La overhead de propagación del trace_id es < 1ms (no impacto medible en latencia) ---

## Endpoints
- Todos los endpoints del sistema propagan el header `X-Trace-ID` - `GET /api/v1/traces/{trace_id}` — Consulta un trace completo (futuro, para dashboard de tracing) ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda usar una biblioteca de tracing como OpenTelemetry para estandarizar la instrumentación - El trace_id se almacena en logs, no en la base de datos transaccional, para no contaminar las tablas de negocio - Para traces muy largos (batch jobs), se puede usar un formato alternativo de trace_id con prefijo "batch-"
