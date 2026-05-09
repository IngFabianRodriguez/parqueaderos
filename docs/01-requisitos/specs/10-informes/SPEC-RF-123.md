# SPEC-10-informes-123 — El sistema debe generar un reporte que muestre todos los vehículos con bloque...

## Metadata
- **RF origen**: RF-123
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin o sede_admin **quiero** consultar un reporte de vehículos bloqueados **para** conocer qué vehículos tienen bloqueo activo, cuál es la razón del bloqueo y desde qué fecha están bloqueados. ---

## Objetivo
El sistema debe generar un reporte que muestre todos los vehículos con bloqueo activo en el parqueadero. Por cada vehículo bloqueado se debe informar: placa, razón del bloqueo, fecha de inicio del bloqueo, sede donde ocurrió, y el usuario o proceso que realizó el bloqueo. ---

## Comportamiento Específico

### Happy Path
1. El usuario solicita el reporte de vehículos bloqueados con filtros (RF-117): sede, rango de fechas (opcional) 2. El `reporting-service` consulta `vehicle-service` para obtener vehículos con `bloqueo_estado = 'active'` 3. Por cada vehículo bloqueado: a. Obtiene datos del vehículo: placa, tipo, marca, modelo b. Obtiene datos del bloqueo: razón, fecha_inicio, sede, usuario_bloqueo c. Si existe, obtiene datos del cliente asociado 4. Calcula totales: cantidad de bloqueos por sede, cantidad por razón 5. Ordena por `fecha_bloqueo` descendente (default) 6. Retorna el reporte ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculos_bloqueados | array | Lista de vehículos con bloqueo activo | | vehiculos_bloqueados[].vehiculo_id | uuid | Identificador del vehículo | | vehiculos_bloqueados[].placa | string | Placa o matrícula del vehículo | | vehiculos_bloqueados[].tipo_vehiculo | string | Carro, moto, etc. | | vehiculos_bloqueados[].marca | string | Marca del vehículo | | vehiculos_bloqueados[].modelo | string | Modelo del vehículo | | vehiculos_bloqueados[].cliente_id | uuid | Propietario del vehículo (si existe) | | vehiculos_bloqueados[].cliente_nombre | string | Nombre del propietario | | vehiculos_bloqueados[].sede_id | uuid | Sede donde está el bloqueo | | vehiculos_bloqueados[].sede_nombre | string | Nombre de la sede | | vehiculos_bloqueados[].razon_bloqueo | string | Razón del bloqueo | | vehiculos_bloqueados[].razon_bloqueo_codigo | string | Código: `morosidad`, `reporte_robo`, `solicitud_propietario`, `otro` | | vehiculos_bloqueados[].fecha_bloqueo | datetime | Fecha y hora cuando se aplicó el bloqueo | | vehiculos_bloqueados[].dias_bloqueado | integer | Días transcurridos desde el bloqueo | | vehiculos_bloqueados[].bloqueado_por | string | Usuario o sistema que realizó el bloqueo | | vehiculos_bloqueados[].notas | string | Notas adicionales del bloqueo | | vehiculos_bloqueados[].ultimo_intento_desbloqueo | datetime | Fecha del último intento de desbloqueo (si existe) | | vehiculos_bloqueados[].estado_desbloqueo | enum | `none`, `solicitado`, `aprobado`, `rechazado` | | totales | object | Agregados del reporte | | totales.cantidad_bloqueados | integer | Total de vehículos con bloqueo activo | | totales.bloqueados_por_sede | array | Conteo por sede | | totales.bloqueados_por_razon | array | Conteo por razón de bloqueo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | vehiculos_bloqueados | array | Lista de vehículos con bloqueo activo | | vehiculos_bloqueados[].vehiculo_id | uuid | Identificador del vehículo | | vehiculos_bloqueados[].placa | string | Placa o matrícula del vehículo | | vehiculos_bloqueados[].tipo_vehiculo | string | Carro, moto, etc. | | vehiculos_bloqueados[].marca | string | Marca del vehículo | | vehiculos_bloqueados[].modelo | string | Modelo del vehículo | | vehiculos_bloqueados[].cliente_id | uuid | Propietario del vehículo (si existe) | | vehiculos_bloqueados[].cliente_nombre | string | Nombre del propietario | | vehiculos_bloqueados[].sede_id | uuid | Sede donde está el bloqueo | | vehiculos_bloqueados[].sede_nombre | string | Nombre de la sede | | vehiculos_bloqueados[].razon_bloqueo | string | Razón del bloqueo | | vehiculos_bloqueados[].razon_bloqueo_codigo | string | Código: `morosidad`, `reporte_robo`, `solicitud_propietario`, `otro` | | vehiculos_bloqueados[].fecha_bloqueo | datetime | Fecha y hora cuando se aplicó el bloqueo | | vehiculos_bloqueados[].dias_bloqueado | integer | Días transcurridos desde el bloqueo | | vehiculos_bloqueados[].bloqueado_por | string | Usuario o sistema que realizó el bloqueo | | vehiculos_bloqueados[].notas | string | Notas adicionales del bloqueo | | vehiculos_bloqueados[].ultimo_intento_desbloqueo | datetime | Fecha del último intento de desbloqueo (si existe) | | vehiculos_bloqueados[].estado_desbloqueo | enum | `none`, `solicitado`, `aprobado`, `rechazado` | | totales | object | Agregados del reporte | | totales.cantidad_bloqueados | integer | Total de vehículos con bloqueo activo | | totales.bloqueados_por_sede | array | Conteo por sede | | totales.bloqueados_por_razon | array | Conteo por razón de bloqueo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Solo se muestran vehículos con `bloqueo_estado = 'active'` a menos que `incluir_desbloqueados=true` 2. El `dias_bloqueado` se calcula como la diferencia entre `HOY` y `fecha_bloqueo` 3. Los totales incluyen la suma exacta de bloqueos activos 4. Se puede exportar según RF-128 5. El reporte se genera en menos de 5 segundos para hasta 5,000 bloqueos activos ---

## Endpoints
- `GET /api/v1/reports/vehicles/blocked` — Genera reporte de vehículos bloqueados - `GET /api/v1/vehicles?blocking_status=active` — Consulta de vehículos bloqueados ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las razones de bloqueo válidas deben definirse en un catálogo: `morosidad`, `reporte_robo`, `solicitud_propietario`, `otro` - Los bloqueos por morosidad se crean automáticamente cuando un cliente entra en el reporte de morosos (RF-122) - Se recomienda que la UI muestre en rojo los vehículos con más de 30 días bloqueados - Este reporte es sensible; se debe registrar quién consultó el reporte en el audit log
