# SPEC-11-app-operador-136 — El operador puede controlar manualmente el estado de cualquier talanquera de ...

## Metadata
- **RF origen**: RF-136
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** abrir o cerrar una talanquera desde la app con confirmación de gesto (doble tap) **para** evitar aperturas accidentales y tener control sobre el acceso de vehículos. ---

## Objetivo
El operador puede controlar manualmente el estado de cualquier talanquera de su sede desde la app móvil. Para evitar activations accidentales, la acción de abrir/cerrar requiere confirmación mediante un gesto de doble tap. El sistema registra cada acción de control con timestamp, operador y resultado. ---

## Comportamiento Específico

### Happy Path
1. El operador accede a la pantalla de control de talánqueras. 2. Se muestra la lista de talánqueras con su estado actual (🔴 Cerrada / 🟢 Abierta). 3. El operador toca la talanquera que desea controlar. 4. Se abre un modal de confirmación con la acción propuesta (ABRIR o CERRAR). 5. El operador debe hacer **doble tap** sobre el botón de confirmar. 6. El sistema envía la instrucción al IoT de la talanquera. 7. La talanquera ejecuta la acción. 8. El sistema actualiza el estado en la UI y registra en el log. 9. Se muestra confirmación visual ("Talanquera abierta" o "Talanquera cerrada"). ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | talanquera_id | UUID | ID de la talanquera | | accion_ejecutada | Enum | ABRIR o CERRAR | | resultado | Enum | EXITO, FALLA, TIMEOUT | | estado_anterior | Enum | Estado antes de la acción | | estado_actual | Enum | Estado después de la acción | | mensaje | String | Descripción del resultado | | timestamp | DateTime | Momento de la ejecución | | ejecutor_id | UUID | ID del operador | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | talanquera_id | UUID | ID de la talanquera | | accion_ejecutada | Enum | ABRIR o CERRAR | | resultado | Enum | EXITO, FALLA, TIMEOUT | | estado_anterior | Enum | Estado antes de la acción | | estado_actual | Enum | Estado después de la acción | | mensaje | String | Descripción del resultado | | timestamp | DateTime | Momento de la ejecución | | ejecutor_id | UUID | ID del operador | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La acción de abrir/cerrar requiere siempre doble tap como confirmación. 2. Un solo tap no ejecuta la acción; se muestra mensaje de confirmación. 3. Si la talanquera está offline, el botón aparece deshabilitado. 4. Si la talanquera está en movimiento, el botón aparece deshabilitado. 5. La acción se completa (éxito o falla) en menos de 5 segundos. 6. El log registra: operador, timestamp, acción, resultado, talanquera. 7. El operador recibe feedback visual inmediato tras el doble tap. 8. Si la talanquera no responde, se muestra error claro con instrucción de verificación manual. ---

## Endpoints
- `POST /api/v1/operator/gates/{id}/control` — Enviar comando (ABRIR/CERRAR) - `GET /api/v1/operator/gates` — Lista de talánqueras con estados - `GET /api/v1/operator/gates/{id}/status` — Estado actual de una talanquera ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El doble tap debe tener un intervalo entre taps de 300ms a 1000ms para ser válido. - Se recomienda usar haptic feedback (vibración) en el dispositivo móvil al confirmarse el doble tap. - El modal debe mostrar claramente qué acción se va a realizar y el nombre de la talanquera.
