# SPEC-13-admin-panel-164 — El panel permite exportar datos de cualquier módulo (usuarios, tickets, pagos...

## Metadata
- **RF origen**: RF-164
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** exportar datos masivamente en diferentes formatos **para** usar la información en sistemas externos o para auditorías. ---

## Objetivo
El panel permite exportar datos de cualquier módulo (usuarios, tickets, pagos, clientes) en formatos estándar: Excel (.xlsx), CSV, y PDF. Las exportaciones pueden ser completas o filtradas. ---

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
1. El archivo se genera en < 30 segundos para hasta 10.000 registros. 2. Para exports grandes, el admin recibe email con link válido 24 horas. 3. Los exports incluyen un resumen con totales y fecha de generación. 4. Los permisos de exportación respetan RBAC (solo datos permitidos para el rol). ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las exportaciones se registran en el log de auditoría. - Los archivos exportados incluyen máscara de datos sensibles (email parcial, teléfono parcial) según RGPD.
