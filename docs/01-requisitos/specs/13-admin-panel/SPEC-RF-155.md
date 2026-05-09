# SPEC-13-admin-panel-155 — El sistema permite configurar tarifas por sede, con estructura flexible que s...

## Metadata
- **RF origen**: RF-155
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** configurar las tarifas de mis sedes **para** definir cómo se cobrará a los clientes por el uso del parqueadero. ---

## Objetivo
El sistema permite configurar tarifas por sede, con estructura flexible que soporta: tarifas por minuto/hora/día, franjas horarias diferentes, tarifas para tipos de espacio distintos, y tarifas especiales para clientes frecuentes o corporativos. ---

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
1. Las tarifas nuevas aplican inmediatamente a tickets que se creen después del cambio. 2. El historial de tarifas se mantiene para auditorías. 3. El admin puede ver un comparativo de tarifas actuales vs. anteriores. 4. Las franjas horarias se aplican correctamente según la hora de entrada del vehículo. 5. Las tarifas corporativas overridean las tarifas base del cliente. 6. El sistema permite configurar tarifas sin límite de complejidad. ---

## Endpoints
- `GET /api/v1/admin/sites/{site_id}/tariffs` — Listar tarifas - `POST /api/v1/admin/sites/{site_id}/tariffs` — Crear tarifa - `PUT /api/v1/admin/tariffs/{id}` — Actualizar tarifa - `DELETE /api/v1/admin/tariffs/{id}` — Eliminar tarifa - `GET /api/v1/admin/tariffs/history/{site_id}` — Historial de cambios ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las tarifas deben mantener historial para resolver disputas de cobros. - Se recomienda nunca eliminar una tarifa, solo inactivarla.
