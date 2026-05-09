# SPEC-13-admin-panel-157 — El panel permite activar/desactivar tipos de notificación (email, SMS, push),...

## Metadata
- **RF origen**: RF-157
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** configurar las notificaciones que se envían a clientes y operadores **para** mantener una comunicación efectiva y personalizada. ---

## Objetivo
El panel permite activar/desactivar tipos de notificación (email, SMS, push), personalizar plantillas de mensajes, y configurar reglas de envío (timing, déclenche). Cada tenant puede adaptar las comunicaciones a su marca. ---

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
1. Cada evento de notificación puede tener plantilla para email, SMS y push. 2. Las variables se reemplazan dinámicamente en el envío. 3. El admin puede hacer pruebas de envío a su propio email/teléfono. 4. Las plantillas tienen historial de cambios. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los SMS tienen límite de 160 caracteres; el sistema los trunca o convierte a MMS. - Se debe guardar versión de cada plantilla para auditoría.
