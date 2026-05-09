# SPEC-11-app-operador-139 — El operador puede interactuar con las alertas activas: resolverlas (tomando a...

## Metadata
- **RF origen**: RF-139
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** resolver o descartar alertas desde la app y ver el historial de alertas de las últimas 24 horas **para** mantener el control de situaciones críticas y tener trazabilidad de las decisiones tomadas. ---

## Objetivo
El operador puede interactuar con las alertas activas: resolverlas (tomando acción correctiva) o descartarlas (con justificación). Además, el operador tiene acceso a un historial de alertas de las últimas 24 horas con el detalle de cada una, incluyendo quién la resolvió, cuándo y con qué acción. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | alerta_id | UUID | Identificador | | tipo | Enum | MORA_VEHICULO, GATE_OFFLINE, ALERTA_MORA | | placa | String | Placa asociada | | ticket_id | UUID | Ticket asociado (si aplica) | | gate_id | UUID | Talanquera asociada (si aplica) | | estado | Enum | ACTIVA, RESUELTA, DESCARTADA, EXPIRADA | | created_at | DateTime | Cuándo se generó | | resolved_at | DateTime | Cuándo se resolvió | | resolved_by | UUID | Operador que resolvió | | accion_tomada | Enum | Acción seleccionada | | observacion | String | Nota del operador | | tiempo_resolucion | Integer | Minutos desde creación hasta resolución | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | alerta_id | UUID | Identificador | | tipo | Enum | MORA_VEHICULO, GATE_OFFLINE, ALERTA_MORA | | placa | String | Placa asociada | | ticket_id | UUID | Ticket asociado (si aplica) | | gate_id | UUID | Talanquera asociada (si aplica) | | estado | Enum | ACTIVA, RESUELTA, DESCARTADA, EXPIRADA | | created_at | DateTime | Cuándo se generó | | resolved_at | DateTime | Cuándo se resolvió | | resolved_by | UUID | Operador que resolvió | | accion_tomada | Enum | Acción seleccionada | | observacion | String | Nota del operador | | tiempo_resolucion | Integer | Minutos desde creación hasta resolución | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El operador puede resolver una alerta en menos de 10 segundos. 2. El operador puede descartar una alerta con justificación obligatoria. 3. Cada resolución/descarte queda registrado con operador, timestamp y acción. 4. Las alertas resueltas desaparecen del panel activo. 5. El historial muestra las alertas de las últimas 24 horas. 6. Las alertas se pueden filtrar por tipo y estado en el historial. 7. Si el operador está offline, la acción se guarda localmente y se sincroniza después. 8. Las alertas no resueltas en 24h se marcan como EXPIRADAS automáticamente. ---

## Endpoints
- `GET /api/v1/operator/alerts/active` — Lista de alertas activas - `GET /api/v1/operator/alerts/history?hours=24` — Historial de alertas - `POST /api/v1/operator/alerts/{id}/resolve` — Resolver alerta - `POST /api/v1/operator/alerts/{id}/dismiss` — Descartar alerta ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las alertas resueltas deben aparecer en el historial con toda la información para auditoría. - Se debe poderExportar el historial a PDF o CSV para reportes del supervisor. - Si una alerta de mora se resuelve con "Pago registrado", debe cerrar efectivamente el ticket asociado.
