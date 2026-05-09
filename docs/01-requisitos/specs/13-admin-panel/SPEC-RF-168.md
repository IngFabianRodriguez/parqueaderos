# SPEC-13-admin-panel-168 — El superadmin tiene un panel dedicado que muestra métricas consolidadas de to...

## Metadata
- **RF origen**: RF-168
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** superadmin del SaaS **quiero** ver y gestionar todos los tenants desde un solo panel **para** tener visibilidad global y tomar decisiones operativas. ---

## Objetivo
El superadmin tiene un panel dedicado que muestra métricas consolidadas de todos los tenants, permite gestionar cuentas, ver uso de recursos, y detectar anomalías. ---

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
1. El dashboard carga en < 5 segundos. 2. Los datos se actualizan cada 15 minutos (no real-time). 3. Superadmin puede exportar la lista completa de tenants a CSV. 4. Las métricas de un tenant específico son comparables con el promedio. 5. El acceso a este panel requiere rol SUPERADMIN explícitamente. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Este panel es exclusivamente para el equipo de ParkCore (superadmins del SaaS), no para admins de tenant.
