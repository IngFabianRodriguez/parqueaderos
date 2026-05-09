# SPEC-12-app-cliente-142 — El sistema debe mostrar al cliente, desde la app móvil, la disponibilidad en ...

## Metadata
- **RF origen**: RF-142
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** ver la disponibilidad de espacios en tiempo real por sede y zona **para** saber con anticipación dónde hay lugar y planificar mi visita. ---

## Objetivo
El sistema debe mostrar al cliente, desde la app móvil, la disponibilidad en tiempo real de espacios de parqueo discriminada por sede y por zona dentro de cada sede. Esta información se actualiza automáticamente cada 30 segundos o mediante pull-to-refresh. ---

## Comportamiento Específico

### Happy Path
1. El cliente abre la vista de "Disponibilidad" en la app. 2. El sistema obtiene la ubicación actual del cliente (siolocation) para sugerencia de sede más cercana, o muestra todas las sedes del tenant. 3. El cliente selecciona una sede del listado. 4. El sistema consulta el servicio de espacios y devuelve la disponibilidad por zona (libres, ocupados, totales, en mantenimiento). 5. La app presenta la información como tarjetas por zona o un mapa interactivo con indicadores de color (verde=disponible, amarillo=pocos espacios, rojo=lleno). 6. El cliente puede pulsar sobre una zona para ver el detalle de espacios individuales. 7. La información se refresca automáticamente cada 30 segundos o mediante pull-to-refresh. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | UUID | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | zonas | array | Lista de zonas con disponibilidad | | zona_id | UUID | Identificador de la zona | | zona_nombre | string | Nombre de la zona | | espacios_totales | int | Total de espacios en la zona | | espacios_libres | int | Espacios actualmente libres | | espacios_ocupados | int | Espacios actualmente ocupados | | espacios_mantenimiento | int | Espacios en mantenimiento | | porcentaje_disponibilidad | decimal | Porcentaje de espacios libres | | ultima_actualizacion | timestamp | Fecha/hora de la última actualización de estado | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | UUID | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | zonas | array | Lista de zonas con disponibilidad | | zona_id | UUID | Identificador de la zona | | zona_nombre | string | Nombre de la zona | | espacios_totales | int | Total de espacios en la zona | | espacios_libres | int | Espacios actualmente libres | | espacios_ocupados | int | Espacios actualmente ocupados | | espacios_mantenimiento | int | Espacios en mantenimiento | | porcentaje_disponibilidad | decimal | Porcentaje de espacios libres | | ultima_actualizacion | timestamp | Fecha/hora de la última actualización de estado | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede ver la lista de sedes disponibles ordenadas por cercanía. 2. Al seleccionar una sede, se muestran todas sus zonas con conteo de espacios libres/ocupados. 3. La información de disponibilidad se actualiza automáticamente cada 30 segundos. 4. El cliente puede hacer pull-to-refresh para forzar una actualización inmediata. 5. Los indicadores de color reflejan el estado: verde (>20% libre), amarillo (1-20%), rojo (0%). 6. Los datos mostrados tienen un margen de edad máximo de 5 minutos; si los datos son más antiguos, se advierte al usuario. 7. La consulta de disponibilidad no toma más de 3 segundos en presentar resultado inicial. ---

## Endpoints
- `GET /api/v1/cliente/sedes` — Lista sedes disponibles para el cliente - `GET /api/v1/cliente/sedes/{sede_id}/disponibilidad` — Obtiene disponibilidad por zonas de una sede - `GET /api/v1/cliente/sedes/{sede_id}/zonas/{zona_id}/espacios` — Detalle de espacios individuales de una zona ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La disponibilidad se calcula a partir del último evento de entrada/salida registrado por los dispositivos ANPR o sensores de ocupación. - Se debe implementar polling o WebSocket para actualizaciones en tiempo real desde el backend. - En zonas con más de 100 espacios, se permite agrupar visualmente para mejorar rendimiento.
