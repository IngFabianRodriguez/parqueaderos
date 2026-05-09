# SPEC-14-conciliacion-170 — El sistema debe aplicar un umbral automático del 0

## Metadata
- **RF origen**: RF-170
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sistema **quiero** marcar automáticamente como "en_discrepancia" toda diferencia mayor al 0.5% entre el efectivo esperado y el efectivo real **para** que el operador y el administrador detecten problemas de caja oportunamente. ---

## Objetivo
El sistema debe aplicar un umbral automático del 0.5% sobre el total de efectivo esperado. Cuando la diferencia calculada exceda este umbral (ya sea por sobrante o faltante), el registro de conciliación debe marcarse con estado "en_discrepancia" y generar una notificación al administrador de sede. ---

## Comportamiento Específico

### Happy Path
1. Sistema completa el cálculo de conciliación (RF-169) 2. Sistema obtiene el valor de diferencia y el total esperado 3. Sistema calcula porcentaje = (|diferencia| / total_esperado) * 100 4. Sistema compara porcentaje con umbral = 0.5% 5. Si porcentaje > umbral: a. Sistema actualiza estado_conciliacion = "en_discrepancia" b. Sistema genera alerta con detalles de la diferencia c. Sistema envía notificación push/email al administrador de sede d. Sistema registra en audit log: operador, turno, diferencia, timestamp 6. Si porcentaje <= umbral: a. Sistema mantiene estado_conciliacion = "conciliado" b. No se genera alerta automática ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | estado_conciliacion | Enum | "conciliado" / "en_discrepancia" | | porcentaje_diferencia | Decimal | Porcentaje de la diferencia | | umbral_aplicado | Decimal | Valor del umbral usado (0.5) | | alerta_generada | Boolean | Si se generó alerta | | notificacion_enviada | Boolean | Si se envió notificación al admin | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | estado_conciliacion | Enum | "conciliado" / "en_discrepancia" | | porcentaje_diferencia | Decimal | Porcentaje de la diferencia | | umbral_aplicado | Decimal | Valor del umbral usado (0.5) | | alerta_generada | Boolean | Si se generó alerta | | notificacion_enviada | Boolean | Si se envió notificación al admin | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Toda diferencia mayor al 0.5% en valor absoluto se marca como "en_discrepancia" 2. Diferencias de exactamente 0.5% NO se marcan como discrepancia 3. El cálculo del porcentaje usa el total esperado como base 4. Se genera notificación al admin dentro de los 30 segundos de detectada la discrepancia 5. El registro de auditoría se crea con operador, turno, monto y tipo de diferencia ---

## Endpoints
- `POST /api/v1/conciliacion/turno/{turno_id}/marcar-discrepancia` — Marcar manualmente como discrepancia - `GET /api/v1/conciliacion/discrepancias` — Listar todas las discrepancias abiertas ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El umbral de 0.5% es configurable por el tenant_admin (ver RF-166) - La notificación al administrador debe incluir: operador, turno, diferencia en monto y porcentaje, link a la conciliación - Se diferencian discrepancias por sobrante (dinero de más) vs faltante (dinero de menos)
