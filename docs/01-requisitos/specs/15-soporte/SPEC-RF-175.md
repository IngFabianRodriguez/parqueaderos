# SPEC-15-soporte-175 — Permitir que cualquier cliente autenticado pueda reportar incidentes, consult...

## Metadata
- **RF origen**: RF-175
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente de la app **quiero** crear un ticket de soporte describiendo mi problema **para** recibir ayuda del equipo de atención del parqueadero. ---

## Objetivo
Permitir que cualquier cliente autenticado pueda reportar incidentes, consultas o problemas relacionados con el uso del sistema de parqueo a través de la creación de un ticket que será asignado y atendido por el personal de soporte de la sede. ---

## Comportamiento Específico

### Happy Path
1. Cliente accede a sección "Ayuda / Soporte" desde el menú principal de la app 2. Sistema presenta formulario de creación de ticket con campos: categoría, assunto, descripción, prioridad (opcional), imágenes adjuntas (opcional) 3. Cliente selecciona categoría del ticket (problema de pago, incidencia en entrada/salida, consulta de facturación, otro) 4. Cliente escribe título y descripción detallada del problema 5. Cliente adjunta hasta 3 imágenes opcionales (capturas de pantalla, fotos del vehículo, etc.) 6. Cliente selecciona prioridad: "baja", "media" (default), "alta" 7. Cliente presiona "Enviar ticket" 8. Sistema valida que todos los campos requeridos estén completos 9. Sistema crea ticket en base de datos con: `cliente_id`, `sede_id`, `fecha_creacion`, `estado=abierto`, `fecha_limite_sla` 10. Sistema calcula `fecha_limite_sla` según prioridad (alta: 4h, media: 24h, baja: 72h) 11. Sistema envía push notification al operador de sede confirmando nuevo ticket 12. Sistema devuelve al cliente pantalla de confirmación con número de ticket y tiempo estimado ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | Identificador único del ticket creado | | numero_ticket | string | Número legible para el cliente (formato: TK-YYYYMMDD-XXXX) | | estado | enum | abierto | | fecha_limite_sla | datetime | Fecha/hora límite para primera respuesta | | mensaje_confirmacion | string | Mensaje de confirmación al cliente | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | Identificador único del ticket creado | | numero_ticket | string | Número legible para el cliente (formato: TK-YYYYMMDD-XXXX) | | estado | enum | abierto | | fecha_limite_sla | datetime | Fecha/hora límite para primera respuesta | | mensaje_confirmacion | string | Mensaje de confirmación al cliente | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Cliente puede crear un ticket de soporte en menos de 3 minutos desde que accede a la sección "Ayuda" 2. Ticket queda registrado en base de datos con todos los campos obligatorios y opcionales correctamente almacenados 3. Cliente recibe push notification de confirmación dentro de 10 segundos de creado el ticket 4. Operador de sede ve el nuevo ticket en su panel de soporte inmediatamente después de la creación 5. Número de ticket mostrado al cliente es único y consultable posteriormente 6. El sistema calcula correctamente la fecha límite SLA según la prioridad seleccionada ---

## Endpoints
- `POST /api/v1/soporte/tickets` — Crear nuevo ticket de soporte - `POST /api/v1/soporte/tickets/{ticket_id}/archivos` — Subir archivos adjuntos al ticket ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El número de ticket `TK-YYYYMMDD-XXXX` se genera con formato: año(4) mes(2) día(2) guión secuencial(4) empezando en 0001 por día - Las imágenes se almacenan en object storage (S3 compatible) y se referencian por URL en la tabla de archivos - El campo `sede_id` se infiere del `cliente_id` consultando la última transacción del cliente para asociar el ticket al dominio correcto
