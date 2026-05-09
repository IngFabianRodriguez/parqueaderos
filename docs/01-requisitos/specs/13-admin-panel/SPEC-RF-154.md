# SPEC-13-admin-panel-154 — El panel permite crear sedes, configurar sus datos básicos (nombre, dirección...

## Metadata
- **RF origen**: RF-154
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** crear y configurar las sedes (parquesaderos) de mi cuenta **para** gestionar la infraestructura de cada ubicación. ---

## Objetivo
El panel permite crear sedes, configurar sus datos básicos (nombre, dirección, horarios), tipos de espacios disponibles, tarifas base, y asociar dispositivos (talanqueras, cámaras ANPR). Cada sede es una entidad independiente con su propia disponibilidad. ---

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
1. El admin puede crear una sede con todos sus espacios y dispositivos en menos de 2 minutos. 2. La disponibilidad de espacios se calcula en tiempo real (< 5 segundos). 3. Cada cambio en configuración de sede queda registrado en auditoría. 4. Los dispositivos asociados muestran su estado (online/offline) en la vista de sede. 5. Los horarios se aplican correctamente en validaciones de tickets. 6. El admin puede inactivar una sede sin eliminar datos históricos. 7. Los espacios pueden reconfigurarse sin afectar tickets abiertos. ---

## Endpoints
- `POST /api/v1/admin/tenants/{tenant_id}/sites` — Crear sede - `GET /api/v1/admin/tenants/{tenant_id}/sites` — Listar sedes - `GET /api/v1/admin/sites/{id}` — Detalle de sede - `PUT /api/v1/admin/sites/{id}` — Actualizar sede - `PUT /api/v1/admin/sites/{id}/spaces` — Configurar espacios - `PUT /api/v1/admin/sites/{id}/devices` — Asociar dispositivos - `PUT /api/v1/admin/sites/{id}/schedule` — Configurar horarios ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los horarios definidos aquí pueden reemplazarse temporalmente por días festivos (festivos nacionales no se configuran manualmente, se importan de fuente externa). - La cantidad de espacios no puede ser 0; mínimo 1. - Los dispositivos deben estar previamente registrados en el sistema (RF-109+).
