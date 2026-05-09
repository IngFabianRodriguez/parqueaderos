# SPEC-13-admin-panel-159 — El panel de administración muestra métricas clave en tiempo real: espacios di...

## Metadata
- **RF origen**: RF-159
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** ver un dashboard con las métricas más importantes de mi operación **para** tomar decisiones informadas. ---

## Objetivo
El panel de administración muestra métricas clave en tiempo real: espacios disponibles, tickets abiertos, ingresos del día, vehículos bloqueados, y alertas. Los datos se actualizan automáticamente sin necesidad de recargar. ---

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
1. El dashboard carga en < 3 segundos. 2. Las métricas se actualizan sin recargar la página. 3. Admin puede filtrar por sede. 4. Superadmin ve métricas de todos los tenants. 5. Se puede exportar el resumen en PDF. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las métricas históricas se acceden desde el módulo de Informes (RF-128+).
