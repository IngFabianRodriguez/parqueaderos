# SPEC-15-soporte-179 — Recolectar feedback estructurado del cliente al finalizar cada transacción de...

## Metadata
- **RF origen**: RF-179
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** calificar mi experiencia después de cada transacción de parqueo **para** que el operador sepa cómo fue mi experiencia y pueda mejorar el servicio. ---

## Objetivo
Recolectar feedback estructurado del cliente al finalizar cada transacción de parqueo (salida del vehículo), mediante una calificación de 1-5 estrellas y un campo de comentario opcional. El sistema debe enviar la solicitud automáticamente después de que se confirma el pago y la salida. ---

## Comportamiento Específico

### Happy Path
1. Cuando se confirma la salida del vehículo y el pago está completado, sistema registra `transaccion_completada_at` 2. Sistema espera 30 segundos para permitir que el cliente abandone la zona de influencia de la talanquera 3. Sistema envía push notification al cliente con título "Cómo estuvo tu parqueo?" y cuerpo "Cuéntanos tu experiencia en [nombre_sede] para ayudar-nos a mejorar" 4. Notificación incluye botón "Calificar ahora" que abre la interfaz de feedback 5. Si el cliente no tiene push habilitadas, se envía email con link directo a la encuesta 6. Cliente ve pantalla de feedback con: - Nombre de la sede y fecha/hora de la transacción - Calificación: 5 estrellas (excelente) a 1 estrella (muy malo) - Campo opcional: "Cuéntanos qué te gustó o qué podemos mejorar" (texto 500 máx) - Botón "Enviar" 7. Cliente selecciona estrellas y opcionalmente escribe comentario 8. Cliente presiona "Enviar" 9. Sistema almacena feedback y calcula/actualiza NPS del cliente 10. Sistema muestra mensaje de agradecimiento y cierra la interfaz 11. Si el cliente no responde en 24 horas, sistema reintenta hasta 2 veces más (días 2 y 3) 12. Si después de 72 horas no hay respuesta, el feedback queda como "no respondido" para métricas ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | feedback_id | uuid | Identificador único del feedback | | transaccion_id | uuid | Transacción asociada | | cliente_id | uuid | Cliente que respondió | | sede_id | uuid | Sede donde ocurrió | | calificacion | integer | 1-5 estrellas | | comentario | text | Comentario del cliente (puede ser null) | | NPS_calculado | integer | NPS del cliente después de esta calificación (-100 a 100) | | estado | enum | completado, pendiente, no_respondido | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | feedback_id | uuid | Identificador único del feedback | | transaccion_id | uuid | Transacción asociada | | cliente_id | uuid | Cliente que respondió | | sede_id | uuid | Sede donde ocurrió | | calificacion | integer | 1-5 estrellas | | comentario | text | Comentario del cliente (puede ser null) | | NPS_calculado | integer | NPS del cliente después de esta calificación (-100 a 100) | | estado | enum | completado, pendiente, no_respondido | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Sistema envía solicitud de feedback a todo cliente que completa una transacción exitosa 2. Cliente puede completar la encuesta en menos de 30 segundos 3. Feedback queda almacenado y visible para el operador de la sede dentro de 1 minuto de ser enviado 4. Calificación de 1-2 estrellas genera alerta inmediata al operador 5. Sistema reintenta hasta 3 veces si el cliente no responde en las primeras 72 horas 6. El NPS del cliente se recalcula con cada nuevo feedback recibido 7. Reporte de calificaciones está disponible en dashboard del operador (ver RF-180) ---

## Endpoints
- `POST /api/v1/feedback/transacciones` — Crear registro de feedback - `GET /api/v1/feedback/transacciones/{transaccion_id}` — Ver feedback de una transacción - `GET /api/v1/soporte/tickets/{ticket_id}/feedback` — Ver feedback relacionado a ticket ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La notificación push debe incluir el logo del tenant para personalización (RF-048) - Para clientes con múltiples transacciones, solo solicitar feedback 1 vez por semana máximo (evitar spam) - Las calificaciones se agregan por sede para calcular el "rating" de la sede (mostrado en app cliente) - Si el cliente tiene un ticket de soporte abierto para esa transacción, no se envía encuesta hasta que el ticket se resuelva - El sistema debe agrupar calificaciones por semana para no abrumar al operador con alertas individuales - Implementar "smart timing": si el cliente históricamente califica entre 8am-10am, enviar en ese horario
