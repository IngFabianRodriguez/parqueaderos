# SPEC-15-soporte-176 — Proporcionar al operador de sede una interfaz para visualizar, atender y reso...

## Metadata
- **RF origen**: RF-176
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de sede **quiero** ver y atender los tickets de soporte creados por los clientes de mi sede **para** resolver sus problemas de manera eficiente y dentro del SLA comprometido. ---

## Objetivo
Proporcionar al operador de sede una interfaz para visualizar, atender y resolver los tickets de soporte creados por los clientes. El operador debe poder responder al cliente, cambiar el estado del ticket y ver el historial completo de interacciones. ---

## Comportamiento Específico

### Happy Path
1. Operador accede a sección "Tickets de Soporte" desde su panel de operaciones 2. Sistema muestra lista de tickets abiertos ordenados por: prioridad (alta→baja) y fecha_limite_sla (más próximo primero) 3. Operador puede filtrar por: estado (abierto, en_proceso, resuelto, cerrado), categoría, fecha 4. Operador selecciona un ticket para ver detalle completo 5. Sistema muestra: datos del cliente, título, descripción, imágenes adjuntas, historial de chat, transacciones relacionadas (si las hay) 6. Operador puede: - Responder al cliente (agrega mensaje al chat del ticket) - Cambiar estado del ticket (respondido, en_proceso, resuelto, cerrado) - Asignar ticket a otro operador de la sede - Agregar nota interna (visible solo para operadores de la sede) - Marcar ticket como duplicado y fusionar con otro ticket 7. Por cada respuesta o cambio de estado, sistema registra auditoría con: operador_id, timestamp, acción, comentario 8. Sistema envía push notification al cliente informándole sobre la actualización 9. Si el ticket cambia a estado "resuelto", sistema solicita feedback al cliente (ver RF-179) ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | ID del ticket actualizado | | estado | enum | Estado actual del ticket | | ultimarespuesta_at | datetime | Timestamp de la última respuesta | | operador_asignado | string | Nombre del operador actualmente asignado | | historial | array | Lista de eventos/interacciones del ticket | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | ID del ticket actualizado | | estado | enum | Estado actual del ticket | | ultimarespuesta_at | datetime | Timestamp de la última respuesta | | operador_asignado | string | Nombre del operador actualmente asignado | | historial | array | Lista de eventos/interacciones del ticket | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Operador puede ver lista de tickets de su sede con latencia < 2 segundos al cargar 2. Operador puede filtrar y ordenar tickets por cualquier campo disponible 3. Cada respuesta del operador llega como notificación push al cliente en < 5 segundos 4. Cambio de estado se refleja inmediatamente en la lista de tickets del operador 5. Historial completo del ticket es visible para cualquier operador de la sede que acceda al mismo 6. Auditoría de todas las acciones queda registrada y es consultable ---

## Endpoints
- `GET /api/v1/soporte/tickets?sede_id={id}&estado={estado}` — Listar tickets de la sede - `GET /api/v1/soporte/tickets/{ticket_id}` — Obtener detalle de un ticket - `POST /api/v1/soporte/tickets/{ticket_id}/responder` — Enviar respuesta - `PATCH /api/v1/soporte/tickets/{ticket_id}/estado` — Cambiar estado - `PATCH /api/v1/soporte/tickets/{ticket_id}/asignar` — Reasignar ticket ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Un ticket solo puede ser atendido por operadores de la sede a la cual pertenece el cliente que lo creó - Los tickets permanecen bloqueados para edición por el operador que los está atendiendo (lock optimista) - El sistema debe mostrar alerta visual cuando un ticket está próximo a vencer su SLA (warning 1h antes del límite) - Los mensajes entre operador y cliente pueden incluir archivos adjuntos (solo imágenes, max 5MB)
