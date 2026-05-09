# SPEC-13-admin-panel-163 — El panel muestra la lista de clientes con deuda pendiente, permite bloquear v...

## Metadata
- **RF origen**: RF-163
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** gestionar la cartera de morosos y los bloqueos de vehículos **para** proteger la operación y garantizar el cobro. ---

## Objetivo
El panel muestra la lista de clientes con deuda pendiente, permite bloquear vehículos asociados, desbloquear cuando pagan, y ver el historial completo de la cartera de morosidad. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

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
1. El sistema bloquea automáticamente cuando un ticket supera X días pendiente (configurable). 2. El desbloqueo manual requiere justificación registrada en auditoría. 3. Un cliente puede tener múltiples vehículos; el bloqueo es por vehículo. 4. El desbloqueo de un vehículo no libera a otros vehículos bloqueados del mismo cliente. 5. Se envía notificación push/SMS al cliente al bloquear y al desbloquear. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los umbrales de bloqueo automático se configuran por plan (Basic: 3 días, Professional: 7 días, Enterprise: 15 días).
