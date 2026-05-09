# SPEC-13-admin-panel-162 — El panel permite consultar el saldo de las billeteras, agregar fondos manualm...

## Metadata
- **RF origen**: RF-162
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** ver y gestionar las billeteras virtuales de mis clientes **para** garantizar el correcto funcionamiento del prepago. ---

## Objetivo
El panel permite consultar el saldo de las billeteras, agregar fondos manualmente, revertir transacciones, y ver el historial completo de movimientos de cada billetera. ---

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
1. El saldo se actualiza en tiempo real tras cada operación. 2. Toda operación de billetera genera una entrada en el historial. 3. Las revertir crea una transacción negativa que compensa la original. 4. El admin puede bloquear una billetera si detecta fraude. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las operaciones de billetera deben tener doble validación para montos grandes (> $500.000).
