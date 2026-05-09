# SPEC-12-app-cliente-147 — El sistema debe presentar al cliente, desde la app, un historial completo de ...

## Metadata
- **RF origen**: RF-147
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** ver mi historial de transacciones con detalle: fecha, sede, duración, monto y forma de pago **para** tener control de mis gastos en parqueo y poder reclamar en caso de errores. ---

## Objetivo
El sistema debe presentar al cliente, desde la app, un historial completo de todas sus transacciones de parqueo. Cada registro muestra: fecha, sede, vehículo, duración, monto, método de pago y estado de la transacción. El historial es consultable por rango de fechas y exportable. ---

## Comportamiento Específico

### Happy Path
1. El cliente accede a "Mi Cuenta" → "Historial de Transacciones". 2. El sistema muestra las últimas 20 transacciones (paginación infinita). 3. Cada registro muestra: fecha, sede, placa, duración, monto, método de pago, estado. 4. El cliente puede aplicar filtros: - Rango de fechas (desde/hasta). - Sede específica. - Vehículo específico. - Tipo de transacción (prepago, renovación, pago en sitio). 5. El cliente puede pulsar sobre una transacción para ver el detalle completo: - Número de comprobante. - Fecha y hora de entrada (si aplica). - Fecha y hora de salida (si aplica). - Tiempo real de parqueo. - Desglose de tarifas (fracción, topping, etc.). - Método de pago utilizado. - Estado (completada, cancelada, reembolsada). 6. El cliente puede exportar el historial en formato PDF o CSV para un rango de fechas seleccionado. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | transacciones | array | Lista de transacciones | | transaccion_id | UUID | Identificador de la transacción | | parqueo_id | UUID | Identificador del parqueo asociado | | fecha | timestamp | Fecha y hora de la transacción | | sede_nombre | string | Nombre de la sede | | vehiculo_placa | string | Placa del vehículo | | duracion_minutos | int | Duración del parqueo | | monto | decimal | Monto total cobrado | | metodo_pago | string | Tipo de método usado | | ultimos_digitos | string | Últimos 4 dígitos | | estado | string | 'completada', 'cancelada', 'reembolsada' | | tipo | string | 'prepago', 'renovacion', 'pago_sitio', 'ajuste' | | total_elementos | int | Total de transacciones que cumplen los filtros | | total_paginas | int | Número total de páginas | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | transacciones | array | Lista de transacciones | | transaccion_id | UUID | Identificador de la transacción | | parqueo_id | UUID | Identificador del parqueo asociado | | fecha | timestamp | Fecha y hora de la transacción | | sede_nombre | string | Nombre de la sede | | vehiculo_placa | string | Placa del vehículo | | duracion_minutos | int | Duración del parqueo | | monto | decimal | Monto total cobrado | | metodo_pago | string | Tipo de método usado | | ultimos_digitos | string | Últimos 4 dígitos | | estado | string | 'completada', 'cancelada', 'reembolsada' | | tipo | string | 'prepago', 'renovacion', 'pago_sitio', 'ajuste' | | total_elementos | int | Total de transacciones que cumplen los filtros | | total_paginas | int | Número total de páginas | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede ver su historial de transacciones paginado (20 por página). 2. El cliente puede filtrar por rango de fechas, sede y vehículo. 3. Cada transacción muestra: fecha, sede, placa, duración, monto, método de pago, estado. 4. El cliente puede ver el detalle completo de cualquier transacción. 5. El cliente puede exportar su historial a PDF para un rango de fechas. 6. Las transacciones canceladas/reembolsadas se muestran con Monto negativo y estado visible. 7. El cliente puede buscar dentro del historial por placa o sede. 8. La carga inicial del historial no toma más de 3 segundos. ---

## Endpoints
- `GET /api/v1/cliente/transacciones` — Lista transacciones del cliente con filtros - `GET /api/v1/cliente/transacciones/{transaccion_id}` — Detalle de una transacción - `GET /api/v1/cliente/transacciones/exportar?formato=pdf&fecha_desde=X&fecha_hasta=Y` — Exporta historial ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El historial incluye tanto transacciones completadas como canceladas/reembolsadas. - Las transacciones se agrupan por parqueo: prepago inicial + renovaciones = una sesión de parqueo. - La exportación en PDF incluye el logo del tenant y los datos del cliente para uso como comprobante de gastos.
