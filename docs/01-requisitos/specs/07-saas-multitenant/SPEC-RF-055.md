# SPEC-07-055 — Registro de Último Uso de API Key para Auditoría

## Metadata
- **RF origen**: RF-055
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: api-gateway, auth-service, audit-service

---

## User Story
**Como** administrador de un tenant **quiero** ver cuándo se usó por última vez cada API key **para** detectar llaves expuestas o integraciones abandonadas y hacer limpieza de seguridad.

## Objetivo
El sistema debe registrar el timestamp del último uso de cada API key y mantener un log de las últimas N requests realizados con esa key, permitiendo al admin consultar el historial de uso y detectar actividad anómala.

## Comportamiento Específico

### Registro de Uso
1. Cada request que pasa la validación de la API key dispara un registro de uso
2. El API Gateway escribe en Redis:
   - `api_keys.last_used_at = NOW()`
   - `api_keys.request_count += 1`
   - Se appendea a `api_key_logs`: `{timestamp, method, path, status_code, response_time_ms}`
3. Se mantiene un buffer circular de los últimos 1,000 requests por key en Redis
4. Periódicamente (cada hora), se sincroniza el contador a la base de datos principal
5. El admin consulta `GET /api/v1/api-keys/{key_id}/usage` y ve:
   - Resumen: total requests, último uso, requests en las últimas 24h
   - Logs recientes: lista de últimos 100 requests con detalle

### Datos de Uso Registrados
| Campo | Tipo | Descripción |
|-------|------|-------------|
| timestamp | datetime | Momento del request |
| method | string | HTTP method (GET, POST, etc.) |
| path | string | Endpoint solicitado |
| status_code | integer | Código de respuesta HTTP |
| response_time_ms | integer | Tiempo de respuesta en ms |
| ip_address | string | IP origen del request |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Redis caído durante el registro | Fail-open: el request pasa; el log se escribe async a DB cuando恢复 |
| Key no usada nunca | `last_used_at = null`; `total_requests = 0` |
| Logs de key revocada | Se mantienen accesibles por 2 años para auditoría |
| Uso anómalo detectado (spike) | Se genera alerta al admin |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada request exitoso con API key actualiza `last_used_at` en menos de 50ms
2. El admin puede ver el resumen de uso desde Settings > API Keys en tiempo real
3. Los logs de uso muestran los últimos 100 requests con method, path, timestamp, status
4. Se genera alerta si el uso de una key aumenta > 10x en 1 hora vs el promedio histórico

## Endpoints
- `GET /api/v1/api-keys/{key_id}/usage` — Ver resumen de uso y logs
- `GET /api/v1/api-keys/{key_id}/logs` — Ver logs detallados con paginación

## Health Check
- `GET /health` → { "status": "ok" }
