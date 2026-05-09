# SPEC-13-admin-panel-160 — El sistema mantiene un log inmutable de todas las acciones sensibles: creació...

## Metadata
- **RF origen**: RF-160
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** superadmin **quiero** ver el log de auditoría de todas las acciones realizadas en el sistema **para** mantener la trazabilidad y seguridad. ---

## Objetivo
El sistema mantiene un log inmutable de todas las acciones sensibles: creación/modificación/eliminación de usuarios, roles, tenants, sedes, cambios de configuración, y accesos administrativos. Cada entrada registra: quién, qué, cuándo, y valores anteriores/nuevos. ---

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
1. El log de auditoría es inmutable: no se puede editar ni eliminar entradas. 2. Las entradas se Retention mínimo 2 años. 3. La búsqueda/filtro retorna resultados en < 2 segundos. 4. Superadmin ve logs de todos los tenants; admin de tenant solo los suyos. 5. Se puede exportar el log filtrado a CSV. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los logs se almacenan en base de datos separada optimizada para lectura. - Para entornos Enterprise, se puede integrar con SIEM externo.
