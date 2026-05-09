# SPEC-12-app-cliente-145 — El sistema debe permitir al cliente gestionar su lista de vehículos desde la app

## Metadata
- **RF origen**: RF-145
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** agregar, editar y eliminar vehículos de mi cuenta **para** poder usar diferentes Autos al hacer parqueo y mantener mi información actualizada. ---

## Objetivo
El sistema debe permitir al cliente gestionar su lista de vehículos desde la app. Cada vehículo tiene placa, marca, modelo, color y tipo de vehículo. El cliente puede tener hasta un máximo de 5 vehículos por cuenta. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculo_id | UUID | Identificador del vehículo | | placa | string | Placa del vehículo | | marca | string | Marca | | modelo | string | Modelo | | anio | int | Año | | color | string | Color | | tipo | string | Tipo | | es_default | boolean | Si es el vehículo predeterminado del cliente | | estado | string | 'activo' o 'inactivo' | | fecha_creacion | timestamp | Fecha de registro | | fecha_actualizacion | timestamp | Última modificación | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculo_id | UUID | Identificador del vehículo | | placa | string | Placa del vehículo | | marca | string | Marca | | modelo | string | Modelo | | anio | int | Año | | color | string | Color | | tipo | string | Tipo | | es_default | boolean | Si es el vehículo predeterminado del cliente | | estado | string | 'activo' o 'inactivo' | | fecha_creacion | timestamp | Fecha de registro | | fecha_actualizacion | timestamp | Última modificación | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede agregar hasta 5 vehículos a su cuenta. 2. El cliente puede editar todos los campos de un vehículo excepto la placa. 3. El cliente puede eliminar un vehículo, lo cual lo marca como inactivo. 4. La placa se valida contra formato y disponibilidad antes de guardar. 5. El cliente puede marcar un vehículo como "default" para que aparezca primero en cada parqueo. 6. El vehículo default se pre-selecciona automáticamente al hacer un prepago (RF-143). 7. Al eliminar un vehículo con parqueo activo, el vehículo sigue apareciendo en ese parqueo específico. 8. El sistema impide registrar la misma placa dos veces en la plataforma. ---

## Endpoints
- `GET /api/v1/cliente/vehiculos` — Lista los vehículos del cliente - `POST /api/v1/cliente/vehiculos` — Crea un nuevo vehículo - `PUT /api/v1/cliente/vehiculos/{vehiculo_id}` — Actualiza un vehículo - `DELETE /api/v1/cliente/vehiculos/{vehiculo_id}` — Elimina (desactiva) un vehículo - `PUT /api/v1/cliente/vehiculos/{vehiculo_id}/default` — Define el vehículo default ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La placa es el identificador principal para la integración con los lectores ANPR en la entrada/salida. - El vehículo default se usa como sugerencia al cliente al hacer prepago. - Los vehículos inactivos se mantienen en la BD para trazabilidad histórica de parqueos.
