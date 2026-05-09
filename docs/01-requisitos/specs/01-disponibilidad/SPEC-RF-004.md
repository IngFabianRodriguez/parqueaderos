# SPEC-01-004 — Filtros por tipo de espacio

## Metadata
- **RF origen**: RF-004
- **Módulo**: 01-disponibilidad
- **Prioridad**: Media
- **Servicios**: parking-service

---

## User Story
**Como** Cliente (conductor) **quiero** filtrar los espacios disponibles por tipo (cubierta, descubierta, VIP, moto) **para** encontrar rápidamente el tipo de espacio que necesito y conocer la tarifa aplicable.

## Objetivo
Permitir que el cliente filtre la disponibilidad de espacios por tipo de espacio, mostrando únicamente las zonas y espacios que coinciden con el filtro seleccionado. El filtro aplica tanto en la vista de mapa como en la lista de disponibilidad.

## Comportamiento Específico

### Happy Path
1. Cliente abre la vista de disponibilidad de una sede
2. Cliente selecciona un filtro de tipo de espacio en el selector de filtros
3. Sistema recibe GET /api/v1/sedes/{sede_id}/disponibilidad?tipo_espacio=cubierta
4. Sistema filtra espacios donde tipo_espacio = 'cubierta' y estado = 'libre'
5. Sistema retorna JSON con zonas que tienen espacios libres del tipo consultado
6. Cliente ve el mapa y lista filtrados

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tipo 'discapacidad' sin espacios | Retorna 200 vacío con mensaje 'No hay espacios accesibles disponibles' |
| Tipo no definido para la sede | Retorna 400 con lista de tipos disponibles |
| Todos los espacios del tipo están ocupados | Retorna 200 con espacios_libres=0 y lista de zonas vacía |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| tipo_espacio | VARCHAR | Tipo: cubierta, descubierta, VIP, moto, discapacidad | Sí |
| zona_id | UUID | Filtrar dentro de una zona específica | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| sede_id | UUID | — |
| tipo_espacio | VARCHAR | — |
| tarifa_base | DECIMAL(10,2) | — |
| espacios_libres | INTEGER | — |
| zonas | ARRAY | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Solo se retornan espacios cuyo tipo coincide exactamente con el filtro
2. La respuesta incluye la tarifa base del tipo de espacio
3. Tiempo de respuesta < 200ms con filtro aplicado

## Endpoints
- `GET /api/v1/sedes/{sede_id}/disponibilidad?tipo_espacio=X` — Filtra por tipo de espacio

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Los tipos válidos se validan contra el enum de la base de datos: cubierta, descubierta, VIP, moto, discapacidad
- La tarifa_base viene de la tabla tarifa asociada al tipo_espacio y sede_id
- Si no existe tarifa definida para el tipo, se retorna tarifa_base=null con un mensaje de advertencia
- El filtro zona_id es opcional: si se especifica, se filtra solo esa zona; si no, se buscan en todas las zonas de la sede