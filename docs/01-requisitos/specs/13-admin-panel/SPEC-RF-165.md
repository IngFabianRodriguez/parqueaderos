# SPEC-13-admin-panel-165 — El panel permite crear, gestionar y revocar API keys para integración, así co...

## Metadata
- **RF origen**: RF-165
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** gestionar las API keys y webhooks de mi cuenta **para** integrar el sistema con aplicaciones de terceros. ---

## Objetivo
El panel permite crear, gestionar y revocar API keys para integración, así como configurar webhooks que recibirán eventos del sistema. ---

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
1. Las API keys se muestran una sola vez al crear; después solo se puede ver el nombre y fecha. 2. Se puede revocar una key sin eliminarla (soft revoke). 3. Los webhooks incluyen retry automático si el endpoint no responde (3 intentos con backoff). 4. Cada webhook tiene log de últimos 100 intentos con estado. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los scopes disponibles: `tickets.read`, `tickets.write`, `payments.read`, `customers.read`, `reports.read`. - La secret del webhook se usa para calcular HMAC-SHA256 del payload.
