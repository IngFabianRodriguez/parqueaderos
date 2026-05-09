# SPEC-01-001 — Mostrar espacios disponibles en tiempo real

## Metadata
- **RF origen**: RF-001
- **Módulo**: 01-disponibilidad
- **Prioridad**: Alta
- **Servicios**: parking-service, api-gateway

---

## User Story
**Como** Cliente (conductor) **quiero** ver cuántos espacios hay disponibles en una sede antes de llegar **para** decidir si voy a ese parqueadero o busco otro.

## Objetivo
El sistema debe consultar en tiempo real el conteo de espacios libres, ocupados, en mantenimiento y reservados por cada sede, y actualizar la información en máximo 5 segundos cada vez que ocurre un ingreso o salida de vehículo.

## Comportamiento Específico

### Happy Path
1. Cliente abre la app y selecciona una sede del mapa o lista
2. Sistema recibe request GET /api/v1/sedes/{sede_id}/disponibilidad
3. Sistema consulta la tabla espacio contando por estado
4. Sistema agrupa los resultados por zona_id y calcula totales
5. Sistema retorna JSON con conteos y desglose por zona
6. Si el cliente tiene websocket activo, se le envía la actualización en tiempo real

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Sede no existe | Retorna 404 con mensaje 'Sede no encontrada' |
| Sede inactiva | Retorna 404 (se trata como no existente) |
| Tenant suspendido (churned) | Retorna 403 'Tenant suspendido, contacte a soporte' |
| Base de datos no disponible | Retorna 503 'Servicio no disponible' |
| 0 espacios definidos para la sede | Retorna 200 con totales en 0 y mensaje de configuración pendiente |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede consultada | Sí |
| incluye_zonas | BOOLEAN | Incluir desglose por zona (default: true) | No |
| tipo_espacio | VARCHAR | Filtrar por tipo: cubierta, descubierta, VIP, moto | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| sede_id | UUID | Identificador de la sede |
| total | INTEGER | Capacidad total de la sede |
| libres | INTEGER | Espacios actualmente libres |
| ocupados | INTEGER | Espacios ocupados |
| mantenimiento | INTEGER | Espacios en mantenimiento |
| reservados | INTEGER | Espacios reservados |
| tasa_ocupacion | DECIMAL(5,2) | Porcentaje de ocupación |
| ultima_actualizacion | TIMESTAMP | Última actualización |
| zonas | ARRAY | Array de objetos con disponibilidad por zona |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. El tiempo entre que ocurre un registro de entrada/salida y que el conteo se refleja no excede 5 segundos
2. La consulta responde en menos de 200ms para sedes con hasta 500 espacios
3. El sistema soporta al menos 100 consultas concurrentes por sede sin degradación
4. La tasa de ocupación se calcula con 2 decimales de precisión

## Endpoints
- `GET /api/v1/sedes/{sede_id}/disponibilidad` — Disponibilidad global de la sede
- `GET /api/v1/sedes/{sede_id}/zonas/{zona_id}/disponibilidad` — Disponibilidad por zona
- `WS /ws/sedes/{sede_id}/disponibilidad` — WebSocket para actualizaciones en tiempo real

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- La tasa de ocupación = (ocupados / total) * 100, redondeado a 2 decimales
- Cuando no hay espacios definidos, se retorna con todos los contadores en 0 pero con HTTP 200
- Los espacios reservados son aquellos asignados a reservas activas (RF-RESERVA-XXX futuro)