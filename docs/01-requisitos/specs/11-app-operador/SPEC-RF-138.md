# SPEC-11-app-operador-138 — La app móvil del operador recibe push notifications en tiempo real ante tres ...

## Metadata
- **RF origen**: RF-138
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** recibir notificaciones push en mi app cuando occuran eventos críticos **para** tomar acción inmediata y mantener la operación fluida. ---

## Objetivo
La app móvil del operador recibe push notifications en tiempo real ante tres tipos de alertas críticas: (1) vehículos lleva más de X horas sin pago ( mora ), (2) una talanquera está offline, y (3) alerta de mora de pago. Estas notificaciones permiten al operador actuar antes de que la situación escalar. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

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
1. Las notificaciones llegan al operador en menos de 10 segundos tras el evento. 2. Cada notificación contiene acción directa (touch) que navega al contexto correcto. 3. Las notificaciones de mora se repiten cada X minutos hasta que se resolvieran. 4. El operador puede silenciar/deshabilitar tipos específicos de notificaciones. 5. Las notificaciones de talanquera offline tienen prioridad sobre las de mora. 6. El badge de la app muestra el número de alertas pendientes. 7. Al abrir la app, se muestra un panel de alertas pendientes si hay más de 0. 8. Las notificaciones funcionan cuando la app está en background. ---

## Endpoints
- `POST /api/v1/notifications/push` — Envío de push notification (interno) - `GET /api/v1/operator/notifications` — Lista de notificaciones no leídas - `PUT /api/v1/operator/notifications/{id}/read` — Marcar como leída - `PUT /api/v1/operator/notifications/preferences` — Actualizar preferencias ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se debe implementar Firebase Cloud Messaging (FCM) o similar para push notifications. - Las notificaciones deben tener deep links hacia las pantallas específicas de la app. - Se debe guardar un log local de todas las notificaciones recibidas para auditoría. - El sonido y vibración para cada tipo de alerta debe ser configurable.
