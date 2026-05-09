# SPEC-14-conciliacion-173 — Al cerrarse un turno, el sistema debe generar un documento PDF oficial que co...

## Metadata
- **RF origen**: RF-173
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de caja **quiero** que el sistema genere un reporte de cierre de turno en PDF con mi firma digital **para** dejar documentado oficialmente el fin de mi turno con validez legal y auditoría. ---

## Objetivo
Al cerrarse un turno, el sistema debe generar un documento PDF oficial que contenga todos los datos relevantes del turno: resumen de ingresos, conciliaciones, alertas atendidas, y una firma digital del operador basada en sus credenciales. El PDF debe ser generable, descargable e inmutable. ---

## Comportamiento Específico

### Happy Path
1. Sistema detecta cierre de turno exitoso (RF-172 completado) 2. Sistema recolecta todos los datos del turno: a. Datos del operador (nombre, ID, sede) b. Horario del turno (inicio, fin, duración) c. Resumen de transacciones (pasajes, recargas, otros) d. Aperturas de talanquera con montos y horas e. Conciliación: total esperado, total real, diferencia f. Alertas atendidas durante el turno g. Justificaciones registradas (si las hay) 3. Sistema genera hash de los datos para integridad 4. Sistema genera firma digital del operador: a. Usa certificado digital del operador (o clave privada derivada de password) b. Genera firma sobre el hash de los datos 5. Sistema genera documento PDF con estructura: - Header: Logo de la empresa, nombre del reporte, fecha/hora - Sección 1: Datos del turno y operador - Sección 2: Resumen de ingresos por categoría - Sección 3: Detalle de aperturas de talanquera - Sección 4: Resultado de conciliación - Sección 5: Alertas atendidas - Sección 6: Firma digital (código hash + timestamp) - Footer: Página, total de páginas, hash del documento 6. Sistema almacena el PDF con referencia en la base de datos 7. Sistema permite al operador descargar el PDF 8. Sistema adjunta el PDF en la notificación de cierre al admin (RF-174) ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | reporte_id | UUID | Identificador único del reporte | | archivo_pdf | Binary | Contenido del PDF generado | | url_descarga | String | URL para descarga del PDF | | hash_documento | String | Hash SHA-256 del PDF para verificación | | firma_digital | String | Firma digital del operador sobre los datos | | timestamp_generacion | Timestamp | Fecha y hora de generación | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | reporte_id | UUID | Identificador único del reporte | | archivo_pdf | Binary | Contenido del PDF generado | | url_descarga | String | URL para descarga del PDF | | hash_documento | String | Hash SHA-256 del PDF para verificación | | firma_digital | String | Firma digital del operador sobre los datos | | timestamp_generacion | Timestamp | Fecha y hora de generación | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El PDF se genera automáticamente al cerrar el turno sin intervención manual 2. El PDF contiene todos los datos de resumen del turno sin excepción 3. La firma digital es verificable criptográficamente 4. El PDF es descargable por el operador y el admin 5. El hash del PDF se almacen para verificación de integridad 6. El tamaño del PDF no excede 5MB 7. El PDF se genera en menos de 30 segundos ---

## Endpoints
- `GET /api/v1/reportes/cierre/{turno_id}` — Obtener URL de descarga del PDF - `GET /api/v1/reportes/cierre/{reporte_id}/descargar` — Descargar el PDF - `POST /api/v1/reportes/cierre/{turno_id}/regenerar` — Regenerar PDF (solo admin) - `GET /api/v1/reportes/cierre/{turno_id}/verificar` — Verificar integridad y firma ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La firma digital usa clave privada del operador derivada de su contraseña mediante PBKDF2 - El PDF debe cumplir con estándar PDF/A para archivo a largo plazo - Se debe poder verificar la firma digital sin necesidad del sistema original - El hash del documento se calcula sobre el PDF completo antes de cualquier modificación
