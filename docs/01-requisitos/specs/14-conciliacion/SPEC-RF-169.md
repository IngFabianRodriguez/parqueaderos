# SPEC-14-conciliacion-169 — El sistema debe calcular y mostrar la diferencia entre el dinero físico conta...

## Metadata
- **RF origen**: RF-169
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de caja **quiero** consultar el total de efectivo esperado versus el registrado en mi turno **para** identificar discrepancias antes del cierre. ---

## Objetivo
El sistema debe calcular y mostrar la diferencia entre el dinero físico contado en caja versus el total de transacciones registradas (cobros de pasaje, recargas, etc.) durante un turno, permitiendo al operador verificar su gestión antes de cerrar. ---

## Comportamiento Específico

### Happy Path
1. Operador accede al módulo de conciliación desde su dashboard 2. Sistema identifica el turno activo del operador (o permite seleccionar uno cerrado) 3. Sistema consulta transacciones del turno: cobros de pasaje, recargas, otros ingresos 4. Sistema consulta aperturas de talanquera registradas en el turno y sus montos 5. Sistema calcula total esperado = suma de todas las transacciones registradas 6. Sistema calcula total físico = suma de apertura inicial + ingresos por aperturas de talanquera 7. Sistema calcula diferencia = total físico - total esperado 8. Sistema muestra resultado con señalización visual si hay diferencia (positiva o negativa) ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | turno_id | UUID | Identificador del turno | | operador_id | UUID | Identificador del operador | | total_esperado | Decimal | Suma de transacciones registradas | | total_fisico | Decimal | Suma de montos en aperturas de talanquera | | diferencia | Decimal | Diferencia entre físico y esperado | | porcentaje_diferencia | Decimal | Porcentaje de la diferencia | | estado_conciliacion | Enum | "conciliado" / "en_discrepancia" / "sin_datos" | | fecha_ultima_conciliacion | Timestamp | Fecha y hora del cálculo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | turno_id | UUID | Identificador del turno | | operador_id | UUID | Identificador del operador | | total_esperado | Decimal | Suma de transacciones registradas | | total_fisico | Decimal | Suma de montos en aperturas de talanquera | | diferencia | Decimal | Diferencia entre físico y esperado | | porcentaje_diferencia | Decimal | Porcentaje de la diferencia | | estado_conciliacion | Enum | "conciliado" / "en_discrepancia" / "sin_datos" | | fecha_ultima_conciliacion | Timestamp | Fecha y hora del cálculo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El sistema calcula correctamente la suma de transacciones por tipo (pasaje, recarga, otros) 2. El sistema calcula correctamente la suma de montos de aperturas de talanquera 3. La diferencia se muestra con 2 decimales y el signo correcto (positivo = sobrante, negativo = faltante) 4. El porcentaje se calcula sobre el total esperado 5. El estado se marca automáticamente según el umbral del 0.5% 6. El operador puede consultar la conciliación en tiempo real durante su turno ---

## Endpoints
- `GET /api/v1/conciliacion/turno/{turno_id}` — Obtener conciliación de un turno - `GET /api/v1/conciliacion/operador/{operador_id}/actual` — Obtener conciliación del turno activo - `POST /api/v1/conciliacion/turno/{turno_id}/calcular` — Forzar recálculo de conciliación ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El cálculo considera únicamente transacciones en efectivo; pagos con tarjeta se excluyen del cálculo de efectivo esperado - El umbral del 0.5% es sobre el total de efectivo esperado - Se debe permitir conciliaciones históricas para auditorías
