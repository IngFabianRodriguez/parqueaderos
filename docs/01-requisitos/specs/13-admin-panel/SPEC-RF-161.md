# SPEC-13-admin-panel-161 — El sistema permite guardar la configuración de cualquier reporte (filtros, co...

## Metadata
- **RF origen**: RF-161
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** guardar vistas personalizadas de reportes **para** acceder rápidamente a la información que necesito sin reconfigurar filtros cada vez. ---

## Objetivo
El sistema permite guardar la configuración de cualquier reporte (filtros, columnas, orden) como una vista con nombre. Las vistas guardadas aparecen en el menú del admin para acceso rápido. ---

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
1. Cada usuario ve solo sus propias vistas guardadas. 2. Las vistas guardadas incluyen: filtros, columnas visibles, ordenamiento. 3. Admin puede eliminar o renombrar sus vistas. 4. Las vistas son específicas por módulo de reporte. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las vistas guardadas no son compartibles entre usuarios (funcionalidad futura).
