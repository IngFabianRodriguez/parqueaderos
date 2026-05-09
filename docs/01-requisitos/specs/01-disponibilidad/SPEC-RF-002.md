# SPEC-01-002 — Consultar disponibilidad por zona

## Metadata
- **RF origen**: RF-002
- **Módulo**: 01-disponibilidad
- **Prioridad**: Alta
- **Servicios**: parking-service, api-gateway

---

## User Story
**Como** Cliente (conductor) **quiero** ver cuántos espacios hay disponibles en una zona específica de la sede **para** saber exactamente en qué zona puedo parquear y llegar directo sin buscar.

## Objetivo
Consultar la disponibilidad de espacios desglosada por cada zona dentro de una sede, permitiendo al cliente filtrar y seleccionar la zona que mejor le convenga según tipo de espacio, piso o sección.

## Comportamiento Específico

### Happy Path
1. Cliente selecciona una sede y luego elige filtrar por zona
2. Sistema recibe GET /api/v1/sedes/{sede_id}/zonas
3. Sistema consulta tabla zona para obtener todas las zonas de la sede
4. Para cada zona, sistema cuenta espacios por estado
5. Sistema retorna JSON ordenado con zonas y conteos desglosados
6. Cliente recibe respuesta con zonas ordenadas por disponibilidad descendente

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Sede con solo 1 zona | Retorna esa única zona con disponibilidad completa |
| Zona con 0 espacios libres | Incluye la zona en respuesta ordenada al final con libres=0 |
| Zona en modo mantenimiento completo | Muestra capacidad pero con libres=0 y estado=mantenimiento |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| incluye_tipos | BOOLEAN | Incluir desglose por tipo de espacio (default: true) | No |
| solo_libres | BOOLEAN | Filtrar y retornar solo zonas con espacios libres (default: false) | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| sede_id | UUID | — |
| zonas | ARRAY | Array de objetos zona con disponibilidad |
| zona_id | UUID | — |
| zona_nombre | VARCHAR | — |
| capacidad | INTEGER | — |
| libres | INTEGER | — |
| tipo_soportados | ARRAY | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Todas las zonas de la sede aparecen en la respuesta
2. Zonas se retornan ordenadas por cantidad de espacios libres descendente
3. Tiempo de respuesta P99 < 150ms para sedes con hasta 20 zonas
4. Respuesta incluye desglose por tipo de espacio si incluye_tipos=true

## Endpoints
- `GET /api/v1/sedes/{sede_id}/zonas` — Lista zonas con disponibilidad

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Si `solo_libres=true`, las zonas con 0 espacios libres se excluyen completamente de la respuesta
- Los tipos_soportados se extraen de los espacios físicos de la zona, deduplicados
- En caso de que la sede no tenga zonas definidas, se retorna array vacío con mensaje informativo