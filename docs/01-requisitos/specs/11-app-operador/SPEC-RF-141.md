# SPEC-11-app-operador-141 — El operador puede bloquear un vehículo (impidiendo su salida hasta que se reg...

## Metadata
- **RF origen**: RF-141
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** bloquear o desbloquear un vehículo desde la app con confirmación de contraseña **para** restringir el acceso de vehículos con mora o infracciones y permitir el ingreso cuando el cliente regularice su situación. ---

## Objetivo
El operador puede bloquear un vehículo (impidiendo su salida hasta que se regularice el pago) o desbloquearlo (habilitando nuevamente su salida) desde la app móvil. Ambas acciones requieren confirmación mediante ingreso de contraseña del operador para evitar uso no autorizado. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculo_id | UUID | Identificador | | placa | String | Placa del vehículo | | estado_anterior | Enum | Estado antes de la acción | | estado_nuevo | Enum | Estado después de la acción (BLOQUEADO o ACTIVO) | | accion | Enum | BLOQUEO o DESBLOQUEO | | motivo | String | Motivo registrado | | operador_id | UUID | ID del operador que ejecutó | | timestamp | DateTime | Momento de la acción | | notificacion_enviada | Boolean | Si se pudo enviar notificación al cliente | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculo_id | UUID | Identificador | | placa | String | Placa del vehículo | | estado_anterior | Enum | Estado antes de la acción | | estado_nuevo | Enum | Estado después de la acción (BLOQUEADO o ACTIVO) | | accion | Enum | BLOQUEO o DESBLOQUEO | | motivo | String | Motivo registrado | | operador_id | UUID | ID del operador que ejecutó | | timestamp | DateTime | Momento de la acción | | notificacion_enviada | Boolean | Si se pudo enviar notificación al cliente | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El operador puede bloquear un vehículo en menos de 10 segundos. 2. El operador puede desbloquear un vehículo en menos de 10 segundos. 3. La contraseña del operador es requerida para ambas acciones. 4. El vehículo queda inmediatamente en el nuevo estado tras la confirmación. 5. El log registra: operador, timestamp, motivo, vehículo, estado anterior/nuevo. 6. La acción de desbloqueo solo se permite en vehículos con estado BLOQUEADO. 7. Si el vehículo tiene un ticket abierto al bloquear, se muestra el detalle. 8. El cliente recibe push notification del bloqueo/desbloqueo si es posible. 9. No se permite bloquear un vehículo que ya está bloqueado. ---

## Endpoints
- `POST /api/v1/operator/vehicles/{id}/block` — Bloquear vehículo - `POST /api/v1/operator/vehicles/{id}/unblock` — Desbloquear vehículo - `GET /api/v1/operator/vehicles/{id}/status` — Estado actual del vehículo - `GET /api/v1/operator/vehicles/blocked` — Lista de vehículos bloqueados ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El operador debe poder bloquear desde el perfil del cliente (RF-140) o desde un ticket abierto. - Se recomienda mostrar una animación visual al bloquear/desbloquear para confirmación clara. - El log de bloqueos debe ser inmutable; no se permite editar ni eliminar registros. - Si el vehículo tiene múltiples bloqueos, se muestra el historial completo.
