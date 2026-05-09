# SPEC-08-configuracion-097 — El sistema debe permitir a los administradores de tenant enviar solicitudes d...

## Metadata
- **RF origen**: RF-097
- **Módulo**: 08-configuracion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de tenant **quiero** poder probar el envío de webhooks antes de activarlos **para** asegurarme de que mi endpoint recibe correctamente los eventos y está configurado con la autenticación adecuada. ---

## Objetivo
El sistema debe permitir a los administradores de tenant enviar solicitudes de prueba a sus endpoints de webhook configurados. La prueba envía un payload simulado del evento seleccionado, con la misma estructura y headers (incluyendo autenticación) que usaría el webhook real. El admin puede verificar que su endpoint recibe y procesa correctamente la solicitud. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | test_id | uuid | Identificador de la prueba | | webhook_id | uuid | Webhook probado | | event_type | string | Evento simulado | | status | enum | `success`, `client_error`, `server_error`, `timeout`, `connection_error` | | http_status_code | integer | Código HTTP retornado | | response_time_ms | integer | Tiempo de respuesta en ms | | response_body | string | Primeros 500 chars del body | | request_headers | object | Headers enviados | | request_payload | object | Payload enviado | | error_message | string | Mensaje de error (si aplica) | | signature_sent | string | Firma HMAC enviada (si aplica) | | executed_at | datetime | Timestamp de ejecución | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | test_id | uuid | Identificador de la prueba | | webhook_id | uuid | Webhook probado | | event_type | string | Evento simulado | | status | enum | `success`, `client_error`, `server_error`, `timeout`, `connection_error` | | http_status_code | integer | Código HTTP retornado | | response_time_ms | integer | Tiempo de respuesta en ms | | response_body | string | Primeros 500 chars del body | | request_headers | object | Headers enviados | | request_payload | object | Payload enviado | | error_message | string | Mensaje de error (si aplica) | | signature_sent | string | Firma HMAC enviada (si aplica) | | executed_at | datetime | Timestamp de ejecución | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Un administrador puede enviar una prueba de webhook desde el panel de administración. 2. La prueba envía un payload similar al evento real con indicador de test. 3. Los headers de autenticación (API key, Bearer, HMAC) se envían igual que en producción. 4. El resultado muestra: status code, tiempo de respuesta, y body de respuesta. 5. El admin puede seleccionar el tipo de evento a simular. 6. Se pueden hacer múltiples pruebas secuenciales sin afectar el webhook. 7. Los errores comunes (401, 404, 500, timeout) se muestran con mensajes claros. 8. La firma HMAC-SHA256 del payload de prueba está disponible para verificación del endpoint. ---

## Endpoints
- `POST /api/v1/tenants/{tenant_id}/webhooks/{id}/test` — Enviar prueba - `GET /api/v1/tenants/{tenant_id}/webhooks/{id}/tests` — Ver historial de pruebas - `POST /api/v1/webhooks/test-connection` — Probar conexión sin evento específico ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La prueba de webhook NO activa el webhook para producción; solo valida la configuración. - Se recomienda hacer al menos 3 pruebas exitosas antes de activar un nuevo webhook. - Si el endpoint tiene rate limiting, el admin debe conocerlo para no saturarlo con pruebas. - El payload de prueba incluye `test: true` para que el endpoint pueda identificarlo.
