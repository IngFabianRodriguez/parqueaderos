# SPEC-11-app-operador-137 — La app móvil del operador muestra una vista en tiempo real del estado de toda...

## Metadata
- **RF origen**: RF-137
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** ver el estado en tiempo real de cada talanquera (abierta/cerrada/error/offline) **para** saber cuáles están operativas y cuáles requieren atención. ---

## Objetivo
La app móvil del operador muestra una vista en tiempo real del estado de todas las talánqueras de la sede. Cada talanquera se muestra con un indicador visual claro de su estado, actualizado instantáneamente ante cualquier cambio mediante WebSocket (o polling como fallback). El operador puede tocar una talanquera para ver más detalle. ---

## Comportamiento Específico

### Happy Path
1. El operador abre la pantalla de talánqueras desde el menú o dashboard. 2. El sistema muestra la lista de talánqueras con su estado actual. 3. Cada talanquera se muestra como un card con: - Nombre/identificador de la talanquera. - Tipo: ENTRADA o SALIDA. - Estado visual: color e ícono. - Última actividad (hace X minutos). 4. El sistema mantiene conexión WebSocket para actualizar en tiempo real. 5. Ante cualquier cambio de estado, la UI se actualiza instantáneamente. 6. El operador puede tocar una talanquera para ver el detalle (historial de últimas 10 acciones). ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todos los estados de talánqueras son visibles en una sola pantalla sin scroll horizontal. 2. Los cambios de estado se reflejan en la UI en menos de 2 segundos. 3. El operador puede distinguir el tipo de cada talanquera (entrada/salida). 4. Las talánqueras offline se muestran claramente diferenciadas. 5. El sistema usa WebSocket como canal principal; polling como fallback. 6. Cada talanquera es táctil y abre su historial de últimas acciones. 7. Se muestra el tiempo transcurrido desde la última actividad. 8. La pantalla no se queda en blanco ante fallos de red; siempre hay contenido visible. ---

## Endpoints
- `GET /api/v1/operator/gates` — Lista de talánqueras con estados - `GET /api/v1/operator/gates/{id}` — Detalle de una talanquera - `GET /api/v1/operator/gates/{id}/history` — Último historial de acciones - `WS /ws/v1/operator/gates` — Canal WebSocket para actualizaciones en tiempo real ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La pantalla de talánqueras debe ser accesible como widget rápido desde el dashboard. - Se debe poder filtrar por tipo (solo entradas, solo salidas). - Si una talanquera está en ERROR, debe aparecer primero en la lista (priorización). - El historial de acciones debe incluir: quién la operó, hora, acción, resultado.
