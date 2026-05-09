# SPEC-13-admin-panel-167 — El sistema permite registrar, clasificar, asignar y resolver incidencias repo...

## Metadata
- **RF origen**: RF-167
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** superadmin **quiero** gestionar las incidencias reportadas por los tenants **para** dar soporte eficiente y mantener la calidad del servicio. ---

## Objetivo
El sistema permite registrar, clasificar, asignar y resolver incidencias reportadas por los administradores de tenant. Cada incidencia tiene historial completo de interacciones. ---

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
1. Cada incidencia tiene SLA según prioridad (Crítica: 1h, Alta: 4h, Media: 24h, Baja: 72h). 2. El cliente recibe notificaciones de cambio de estado. 3. Se registra tiempo total de resolución. 4. Las incidencias cerradas se mantienen en historial 90 días. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las categorías de incidencia: BUG, MEJORA, CONSULTA, FACTURACION, INTEGRACION.
