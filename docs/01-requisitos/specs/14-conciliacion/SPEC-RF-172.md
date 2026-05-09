# SPEC-14-conciliacion-172 — El sistema debe permitir al operador de caja cerrar su turno consolidando y m...

## Metadata
- **RF origen**: RF-172
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de caja **quiero** realizar el cierre de mi turno consolidando todos los ingresos, aperturas de talanquera y alertas atendidas **para** dejar el turno correctamente cerrado y permitir que el siguiente operador comience con claridad. ---

## Objetivo
El sistema debe permitir al operador de caja cerrar su turno consolidando y mostrando un resumen completo que incluye: total de ingresos por tipo de transacción, aperturas de talanquera registradas durante el turno, alertas atendidas, y el resultado de la conciliación de efectivo. El cierre solo se completa si la conciliación no tiene discrepancias sin justificar. ---

## Comportamiento Específico

### Happy Path
1. Operador selecciona opción "Cerrar Turno" desde su dashboard 2. Sistema verifica que no existan alertas pendientes sin atender del turno 3. Sistema presenta pantalla de resumen con: a. Total de cobros de pasaje (cantidad y monto) b. Total de recargas (cantidad y monto) c. Total de otros ingresos d. Lista de aperturas de talanquera del turno e. Total de alertas atendidas durante el turno f. Resultado de conciliación (diferencia si existe) 4. Operador confirma los datos visualizados 5. Sistema verifica estado de conciliación: a. Si hay discrepancia sin justificación: mostrar error, no permitir cierre b. Si hay discrepancia con justificación pendiente: mostrar advertencia, permitir cerrar con confirmación adicional c. Si todo está conciliado o justificado: continuar con cierre 6. Operador confirma el cierre definitivo 7. Sistema: a. Actualiza estado del turno a "cerrado" b. Genera reporte de cierre (RF-173) c. Notifica al administrador (RF-174) d. Libera la caja para el siguiente turno 8. Sistema muestra confirmación de cierre exitoso con número de reporte ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | turno_id | UUID | Identificador del turno cerrado | | estado | Enum | "cerrado" | | resumen_turno | Object | Objeto con todos los totales consolidados | | reporte_cierre_id | UUID | Referencia al reporte generado | | timestamp_cierre | Timestamp | Fecha y hora exacta del cierre | | operador_cierre | UUID | ID del operador que realizó el cierre | **Estructura de resumen_turno**: ```json { "ingresos": { "pasajes": { "cantidad": 0, "monto": 0.00 }, "recargas": { "cantidad": 0, "monto": 0.00 }, "otros": { "cantidad": 0, "monto": 0.00 } }, "total_ingresos": 0.00, "aperturas_talanquera": [ { "hora": "HH:MM", "monto": 0.00 } ], "total_aperturas": 0.00, "alertas_atendidas": 0, "conciliacion": { "estado": "conciliado|en_discrepancia|justificado", "diferencia": 0.00 } } ``` ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | turno_id | UUID | Identificador del turno cerrado | | estado | Enum | "cerrado" | | resumen_turno | Object | Objeto con todos los totales consolidados | | reporte_cierre_id | UUID | Referencia al reporte generado | | timestamp_cierre | Timestamp | Fecha y hora exacta del cierre | | operador_cierre | UUID | ID del operador que realizó el cierre | **Estructura de resumen_turno**: ```json { "ingresos": { "pasajes": { "cantidad": 0, "monto": 0.00 }, "recargas": { "cantidad": 0, "monto": 0.00 }, "otros": { "cantidad": 0, "monto": 0.00 } }, "total_ingresos": 0.00, "aperturas_talanquera": [ { "hora": "HH:MM", "monto": 0.00 } ], "total_aperturas": 0.00, "alertas_atendidas": 0, "conciliacion": { "estado": "conciliado|en_discrepancia|justificado", "diferencia": 0.00 } } ``` ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cierre de turno solo se permite si todas las discrepancias están justificadas o aprobadas 2. El resumen muestra exactamente los totales por tipo de transacción 3. El cierre genera un ID único de reporte que se puede consultar posteriormente 4. El operador puede cancelar la operación de cierre en cualquier momento antes de confirmar 5. El sistema impide que se abra un nuevo turno en la misma caja si hay uno abierto 6. El timestamp de cierre es exacto al segundo y no modificable ---

## Endpoints
- `POST /api/v1/turnos/{turno_id}/cerrar` — Cerrar un turno - `GET /api/v1/turnos/{turno_id}/resumen` — Obtener resumen previo al cierre - `GET /api/v1/turnos/{turno_id}/estado` — Consultar estado del turno ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El operador debe tener posibilidad de imprimir el resumen antes de cerrar (sin ser el cierre oficial) - El cierre de turno debe ser irrevocable - no se puede "des cerrar" un turno - El administrador de sede puede cerrar turnos de cualquier operador de su sede - Se debe garantizar que no haya dinero sin registrar al momento del cierre
