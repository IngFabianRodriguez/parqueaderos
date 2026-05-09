# SPEC-10-informes-129 — El sistema debe permitir al usuario configurar programas de generación y entr...

## Metadata
- **RF origen**: RF-129
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede **quiero** programar reportes periódicos (diarios, semanales o mensuales) **para** recibir automáticamente por email los reportes más importantes sin tener que solicitarlos manualmente. ---

## Objetivo
El sistema debe permitir al usuario configurar programas de generación y entrega automática de reportes. Cada programa define: reporte a generar, frecuencia (diaria, semanal, mensual), destinatarios, formato de exportación preferido y hora de envío. El sistema ejecuta los programas en el horario configurado y envía el reporte por email a todos los destinatarios. ---

## Comportamiento Específico

### Happy Path
1. El usuario accede a la sección "Reportes Programados" dentro del módulo de informes. 2. El usuario crea un nuevo programa: a. Selecciona el reporte base (de la lista de reportes disponibles). b. Define los parámetros del reporte (filtros fijos como sede, tipos de datos). c. Selecciona la frecuencia: DIARIA (todos los días a hora específica), SEMANAL (día de semana específico), MENSUAL (día del mes específico). d. Define la hora de envío (formato 24h). e. Agrega destinatarios (emails válidos). f. Selecciona el formato de exportación preferido. 3. El sistema valida los datos y crea el programa en la base de datos con estado ACTIVO. 4. El scheduler ejecuta los programas según su configuración: a. En la hora programada, el sistema genera el reporte con los parámetros configurados. b. El sistema genera la exportación en el formato elegido. c. El sistema envía el email con el archivo adjunto a todos los destinatarios. d. El sistema registra el resultado en el log de entregas (RF-130). 5. Si hay errores, se reintenta hasta 3 veces y se notifica al creador del programa. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | programa_id | UUID | Identificador del programa creado | | nombre | String | Nombre del programa | | reporte_nombre | String | Nombre del reporte base | | frecuencia | Enum | DIARIA, SEMANAL, MENSUAL | | siguiente_ejecucion | DateTime | Timestamp de la próxima ejecución | | estado | Enum | ACTIVO, PAUSADO, ERROR, CANCELADO | | destinatarios_count | Integer | Cantidad de destinatarios configurados | | ultimo_envio | DateTime | Timestamp del último envío exitoso | | creado_por | UUID | ID del usuario que creó el programa | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | programa_id | UUID | Identificador del programa creado | | nombre | String | Nombre del programa | | reporte_nombre | String | Nombre del reporte base | | frecuencia | Enum | DIARIA, SEMANAL, MENSUAL | | siguiente_ejecucion | DateTime | Timestamp de la próxima ejecución | | estado | Enum | ACTIVO, PAUSADO, ERROR, CANCELADO | | destinatarios_count | Integer | Cantidad de destinatarios configurados | | ultimo_envio | DateTime | Timestamp del último envío exitoso | | creado_por | UUID | ID del usuario que creó el programa | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El usuario puede crear programas de reportes con frecuencia diaria, semanal o mensual. 2. Cada programa permite agregar múltiples destinatarios de email. 3. El reporte se genera automáticamente en el horario configurado y se envía por email. 4. El email incluye el archivo adjunto en el formato seleccionado y un resumen en texto del contenido del reporte. 5. El programa puede activarse o pausarse en cualquier momento. 6. El sistema reintenta hasta 3 veces los envíos fallidos con backoff exponencial (1min, 5min, 15min). 7. Los programas de reportes sobreviven a reinicios del servidor (persisten en base de datos). 8. El usuario recibe una notificación si un programa falla 3 veces consecutivas. ---

## Endpoints
- `POST /api/v1/reports/schedules` — Crea un nuevo programa de reporte - `GET /api/v1/reports/schedules` — Lista todos los programas del usuario/sede - `PUT /api/v1/reports/schedules/{id}` — Actualiza un programa existente - `PATCH /api/v1/reports/schedules/{id}/pause` — Pausa un programa - `PATCH /api/v1/reports/schedules/{id}/resume` — Reanuda un programa pausado - `DELETE /api/v1/reports/schedules/{id}` — Elimina un programa ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El scheduler utiliza un cronjob que consulta los programas activos cada minuto. - Los parámetros del reporte son fijados al momento de crear el programa; no se recalculan dinámicamente. - Para reportes que requieren contexto de fecha (ej: "últimos 7 días"), el programa cálcula el rango de fechas en cada ejecución basándose en la frecuencia. - El email enviado incluye: asunto con nombre del reporte y período, cuerpo con resumen ejecutivo de 3-5 líneas, y archivo adjunto. - Si el usuario quiere dejar de recibir un email programado, puede desuscribirse del enlace en el email sin cancelar todo el programa.
