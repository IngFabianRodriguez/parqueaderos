# SPEC-13-admin-panel-158 — El sistema permite registrar dispositivos en cada sede, configurar sus paráme...

## Metadata
- **RF origen**: RF-158
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** registrar y configurar los dispositivos IoT (talanqueras, cámaras ANPR) **para** integrar el hardware con el sistema. ---

## Objetivo
El sistema permite registrar dispositivos en cada sede, configurar sus parámetros de comunicación (IP, puerto), ver su estado en tiempo real, y diagnosticar problemas de conexión. ---

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
1. Un dispositivo solo puede pertenecer a una sede. 2. El sistema marca OFFLINE si no hay heartbeat en 60 segundos. 3. El admin recibe alerta si un dispositivo pasa a estado ERROR. 4. Se puede reconfigurar IP/puerto sin eliminar el dispositivo. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los dispositivos se registran antes de asociarlos a una sede.
