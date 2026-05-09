# SPEC-15-soporte-178 — Implementar un sistema de chat en tiempo real integrado dentro de la app del ...

## Metadata
- **RF origen**: RF-178
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** poder chatear en tiempo real con el operador de soporte **para** resolver rápidamente mi consulta o problema sin necesidad de esperar respuesta por email o ticket formal. ---

## Objetivo
Implementar un sistema de chat en tiempo real integrado dentro de la app del cliente y el panel del operador, permitiendo comunicación instantánea durante la resolución de incidentes de soporte. El chat debe estar vinculado a un ticket específico y mantener historial completo de conversaciones. ---

## Comportamiento Específico

### Happy Path
1. Cliente accede a su ticket de soporte desde la app (ver estado y acceder al chat) 2. Si el ticket está en estado "abierto" o "en_proceso", se habilita botón "Chatear ahora" 3. Cliente presiona "Chatear ahora" y se abre interfaz de chat en tiempo real 4. Sistema establece conexión WebSocket entre cliente y operador asignado al ticket 5. Cliente escribe y envía mensaje; sistema lo transmite al operador vía WebSocket 6. Operador ve el mensaje en su panel de chat en tiempo real (< 1s) 7. Operador escribe respuesta y envía; cliente recibe en su app en tiempo real 8. Si el operador no está conectado, sistema guarda mensaje en BD y envía push notification al operador 9. Cuando operador abre el chat, ve todos los mensajes previos del ticket 10. Cliente puede enviar imágenes (capturas de pantalla del error) hasta 3 imágenes por mensaje 11. Chat puede incluir mensajes de "sistema" (ticket asignado, estado cambiado, etc.) diferenciados visualmente 12. Cuando ticket se cierra, chat queda en modo solo lectura para ambos participantes 13. Historial completo del chat quedaAttached al ticket para referencia futura ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | mensaje_id | uuid | Identificador único del mensaje | | ticket_id | uuid | Ticket al que pertenece | | contenido | text | Contenido del mensaje | | tipo | enum | texto, imagen, sistema | | emisor | object | Datos del emisor (id, nombre, tipo) | | timestamp | datetime | Hora de envío del mensaje | | entregado | boolean | true si fue entregado al destinatario | | leido | boolean | true si el destinatario lo leyó | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | mensaje_id | uuid | Identificador único del mensaje | | ticket_id | uuid | Ticket al que pertenece | | contenido | text | Contenido del mensaje | | tipo | enum | texto, imagen, sistema | | emisor | object | Datos del emisor (id, nombre, tipo) | | timestamp | datetime | Hora de envío del mensaje | | entregado | boolean | true si fue entregado al destinatario | | leido | boolean | true si el destinatario lo leyó | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Mensaje enviado por cliente llega al operador en < 1 segundo (tiempo real) 2. Mensaje enviado por operador llega al cliente en < 1 segundo (tiempo real) 3. Historial de chat persiste y es consultable después de cerrado el ticket 4. Cliente puede enviar imágenes adjuntas en el chat sin errores 5. Sistema de notificaciones push entrega mensaje cuando receptor está offline 6. Chat funciona correctamente bajo mala conectividad (3G) con modo offline 7. Interfaz de chat es responsiva y usable tanto en app móvil como en panel web de operador 8. Indicador visual de "escribiendo..." se muestra cuando el otro participante está escribiendo ---

## Endpoints
- `WebSocket /ws/soporte/tickets/{ticket_id}/chat` — Conexión de chat en tiempo real - `POST /api/v1/soporte/tickets/{ticket_id}/chat/mensajes` — Enviar mensaje (fallback REST) - `GET /api/v1/soporte/tickets/{ticket_id}/chat/mensajes?page={n}` — Obtener historial paginado - `PATCH /api/v1/soporte/tickets/{ticket_id}/chat/mensajes/{mensaje_id}/leido` — Marcar como leído ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El sistema debe usar WebSocket (Socket.io o similar) para comunicación en tiempo real - Para fallback offline, usar polling REST cada 5 segundos como backup - Incluir "typing indicators" (indicador de que el otro está escribiendo) vía WebSocket events - Los mensajes de sistema deben tener estilo visual diferenciado (gris, italic, sin avatar) - Almacenar timestamps en UTC; mostrar en timezone local del espectador - Implementar "read receipts" (marca de leído) cuando el destinatario abre el mensaje - El chat debe permitir anclaje de imágenes del ticket (imágenes adjuntas al problema original)
