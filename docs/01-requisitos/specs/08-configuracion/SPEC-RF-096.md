# SPEC-08-configuracion-096 — El sistema debe permitir a los administradores de tenant configurar uno o más...

## Metadata
- **RF origen**: RF-096
- **Módulo**: 08-configuracion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de tenant **quiero** configurar webhooks salientes con URL, eventos suscritos y headers de autenticación **para** recibir notificaciones en tiempo real en mis propios sistemas cuando ocurran eventos en ParkCore (ingresos, pagos, bloqueos, etc.). ---

## Objetivo
El sistema debe permitir a los administradores de tenant configurar uno o más webhooks salientes. Cada webhook define: la URL de destino, los eventos a los que se suscribe, los headers de autenticación (API key, Bearer token, HMAC signature), y opciones de retry. Cuando ocurre un evento configurado, el sistema envía una petición HTTP POST al endpoint con los datos del evento. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | webhook_id | uuid | Identificador | | name | string | Nombre | | url | string | URL | | events | array | Eventos suscritos | | auth_type | enum | Tipo de autenticación | | active | boolean | Estado | | created_at | datetime | Fecha de creación | | stats | object | `total_deliveries`, `success_rate`, `last_delivery_at` | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | webhook_id | uuid | Identificador | | name | string | Nombre | | url | string | URL | | events | array | Eventos suscritos | | auth_type | enum | Tipo de autenticación | | active | boolean | Estado | | created_at | datetime | Fecha de creación | | stats | object | `total_deliveries`, `success_rate`, `last_delivery_at` | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Un administrador puede crear, editar y eliminar webhooks. 2. Cada webhook puede suscribirse a uno o más eventos. 3. Se soportan 4 tipos de autenticación: none, API key, Bearer token, HMAC-SHA256. 4. Los payloads de los eventos incluyen todos los datos relevantes en JSON. 5. Las solicitudes incluyen header `X-ParkCore-Signature` para verificación de origen. 6. Los reintentos automáticos se ejecutan con backoff exponencial. 7. Cada intento de entrega se registra con: timestamp, status code, response body (si error). 8. Los webhooks se pueden pausar y reanudar sin eliminar la configuración. 9. El sistema notifica al admin cuando un webhook entra en estado `dead`. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/webhooks` — Listar webhooks - `POST /api/v1/tenants/{tenant_id}/webhooks` — Crear webhook - `PUT /api/v1/tenants/{tenant_id}/webhooks/{id}` — Actualizar webhook - `DELETE /api/v1/tenants/{tenant_id}/webhooks/{id}` — Eliminar webhook - `POST /api/v1/tenants/{tenant_id}/webhooks/{id}/pause` — Pausar webhook - `POST /api/v1/tenants/{tenant_id}/webhooks/{id}/resume` — Reanudar webhook - `GET /api/v1/tenants/{tenant_id}/webhooks/{id}/deliveries` — Ver historial de entregas ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los webhooks son síncronos: el evento no se considera "procesado" hasta que el delivery intenta enviarse. - Para eventos de alto volumen (ej: `vehicle.entry`), el admin debe ser consciente del tráfico que generará. - La firma HMAC-SHA256 permite al endpoint verificar que el request vino realmente de ParkCore. - Se recomienda usar HTTPS siempre; HTTP es permitido solo para desarrollo local. - El `X-ParkCore-Signature` header contiene: `sha256=<hmac_hex>` del body completo.
