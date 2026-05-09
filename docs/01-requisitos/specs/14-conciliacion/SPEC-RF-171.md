# SPEC-14-conciliacion-171 — Cuando se detecta una discrepancia entre el efectivo esperado y el real, el o...

## Metadata
- **RF origen**: RF-171
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de caja **quiero** registrar una diferencia de caja con su justificación y evidencia fotográfica **para** dejar documentado el motivo de la discrepancia y que sea auditado por el administrador. ---

## Objetivo
Cuando se detecta una discrepancia entre el efectivo esperado y el real, el operador debe poder registrar una justificación que explique la diferencia, incluyendo descripción del motivo y evidencia fotográfica del dinero contado al momento de la detección. Este registro queda vinculado a la conciliación del turno para auditoría. ---

## Comportamiento Específico

### Happy Path
1. Operador visualiza la conciliación con discrepancia 2. Operador selecciona opción "Registrar Justificación" 3. Sistema presenta formulario con campos: motivo (dropdown), descripción (texto), evidencia (foto) 4. Operador selecciona motivo de lista predefinida: - Error de conteo del operador - Billete falso detectado - Transacción no registrada en sistema - Venta cancelada que no apareció en cierre - Otro (requiere descripción) 5. Operador ingresa descripción ampliada del motivo 6. Operador captura foto del dinero contado mostrando el monto total 7. Sistema valida que la imagen sea legible y del tamaño correcto 8. Sistema almacena la imagen y crea el registro de justificación 9. Sistema vincula la justificación a la conciliación del turno 10. Sistema notifica al administrador de sede sobre la justificación registrada 11. Administrador puede aprobar o rechazar la justificación ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | justificacion_id | UUID | Identificador de la justificación creada | | estado | Enum | "pendiente_aprobacion" / "aprobada" / "rechazada" | | fecha_creacion | Timestamp | Fecha y hora de creación | | administrador_revisor | UUID | ID del admin que revisó (si aplicacble) | | fecha_revision | Timestamp | Fecha y hora de revisión (si aplicable) | | comentario_revision | Text | Comentario del admin al aprobar/rechazar | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | justificacion_id | UUID | Identificador de la justificación creada | | estado | Enum | "pendiente_aprobacion" / "aprobada" / "rechazada" | | fecha_creacion | Timestamp | Fecha y hora de creación | | administrador_revisor | UUID | ID del admin que revisó (si aplicacble) | | fecha_revision | Timestamp | Fecha y hora de revisión (si aplicable) | | comentario_revision | Text | Comentario del admin al aprobar/rechazar | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El operador puede registrar justificación dentro de las 24 horas posteriores al cierre del turno 2. La foto de evidencia debe mostrar claramente los billetes/contado 3. El administrador recibe notificación inmediata de nueva justificación 4. El registro de justificación es inmutable (solo se añade estado de revisión) 5. Se permite adjuntar hasta 3 fotos como evidencia 6. La justificación queda vinculada al turno y operador específico ---

## Endpoints
- `POST /api/v1/conciliacion/justificacion` — Crear justificación de diferencia - `GET /api/v1/conciliacion/justificacion/{justificacion_id}` — Ver detalles de justificación - `PUT /api/v1/conciliacion/justificacion/{justificacion_id}/revisar` — Aprobar o rechazar justificación (admin) - `POST /api/v1/conciliacion/justificacion/{justificacion_id}/evidencia` — Subir foto de evidencia ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las justificaciones aprobadas no modifican el monto de la diferencia, solo la documentan - El admin debe poder rechazar una justificación si el motivo no es válido - Se debe mantener historial completo de todas las justificaciones para auditorías - La foto de evidencia se almacena en object storage (S3/MinIO) con referencia en BD
