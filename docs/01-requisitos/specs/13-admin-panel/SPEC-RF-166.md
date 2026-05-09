# SPEC-13-admin-panel-166 — El panel permite crear tareas programadas: envío de reportes periódicos, noti...

## Metadata
- **RF origen**: RF-166
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** programar tareas automáticas **para** delegar trabajos repetitivos al sistema. ---

## Objetivo
El panel permite crear tareas programadas: envío de reportes periódicos, notificaciones de cumpleaños/vencimientos, y mantenimiento automático de datos. ---

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
1. Las tareas se ejecutan aunque el admin no esté logueado. 2. El sistema registra resultado de cada ejecución (éxito/falla). 3. El admin recibe alerta si una tarea falla 3 veces consecutivas. 4. Se puede pausar/reanudar tareas sin eliminarlas. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El scheduler interno no es para tareas de alta frecuencia; esas van en el motor de workers.
