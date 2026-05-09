# SPEC-09-observabilidad-107 — El sistema debe permitir al `tenant_admin` configurar uno o más canales de no...

## Metadata
- **RF origen**: RF-107
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** `tenant_admin` **quiero** elegir cómo recibir las alertas (email, SMS, Slack, webhook) **para** asegurarme de que el equipo correcto sea notificado por el canal apropiado según la severidad de la alerta. ---

## Objetivo
El sistema debe permitir al `tenant_admin` configurar uno o más canales de notificación para recibir alertas. Los canales disponibles son: email, SMS, Slack, y webhook (HTTP POST a una URL). Cada canal tiene su propia configuración (dirección de email, número de teléfono, workspace de Slack, URL de webhook). Se pueden configurar múltiples canales por alerta, y cada canal puede restringirse a ciertas severidades (ej: CRITICAL por SMS, WARNING por email). ---

## Comportamiento Específico

### Happy Path
1. El `tenant_admin` accede a `Observabilidad → Alertas → Canales de Notificación`. 2. El sistema muestra los canales configurados actualmente. 3. El admin puede agregar un nuevo canal: - Selecciona el tipo: `email`, `sms`, `slack`, `webhook`. - Ingresa la configuración específica (email, teléfono, workspace, URL). - Define a qué severidades aplica: `[CRITICAL]`, `[WARNING]`, `[INFO]`, o cualquier combinación. - Define si el canal está activo o no. 4. El admin puede probar el canal (enviar mensaje de prueba). 5. El canal se guarda en `notification_channels`. 6. Cuando se genera una alerta, el `alerting-service` consulta los canales activos para la severidad de la alerta y envía la notificación a cada uno. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `tenant_admin` puede agregar, editar, eliminar y activar/desactivar canales de notificación. 2. Los canales disponibles son: email, SMS, Slack, webhook. 3. Cada canal tiene configuración específica según el tipo. 4. Cada canal puede filtrar por severidad (ej: solo CRITICAL van por SMS). 5. Se puede probar cada canal con un mensaje de prueba. 6. Las notificaciones incluyen: tipo de alerta, severidad, servicio afectado, timestamp, y link al dashboard. 7. Los canales fallidos se reintentan automáticamente con backoff exponencial. 8. El sistema no envía notificaciones duplicadas en menos de 5 minutos para la misma alerta. 9. Todas las credenciales (tokens, API keys) se almacenan encriptadas. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/notification-channels` — Listar canales - `POST /api/v1/tenants/{tenant_id}/notification-channels` — Crear canal - `PUT /api/v1/tenants/{tenant_id}/notification-channels/{channel_id}` — Actualizar canal - `DELETE /api/v1/tenants/{tenant_id}/notification-channels/{channel_id}` — Eliminar canal - `POST /api/v1/tenants/{tenant_id}/notification-channels/{channel_id}/test` — Probar canal - `PATCH /api/v1/tenants/{tenant_id}/notification-channels/{channel_id}/activate` — Activar - `PATCH /api/v1/tenants/{tenant_id}/notification-channels/{channel_id}/deactivate` — Desactivar ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda que el email incluya un link directo al dashboard de alertas para facilitar la investigación. - Para webhooks, el `auth_type` puede ser `api_key` (envía `X-API-Key` header) o `bearer` (envía `Authorization: Bearer <token>`). - El log de `alert_notifications` debe incluir: canal, alert_id, timestamp_envio, timestamp_ack, status (`SENT`, `FAILED`, `PENDING_RETRY`). - Se debe implementar rate limiting por canal para evitar sobrecargar proveedores (ej: máx 100 SMS/hora). - Las credenciales nunca deben aparecer en logs; usar IDs de credencial en su lugar.
