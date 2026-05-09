# SPEC-11-app-operador-131 — La app móvil del operador debe mostrar en su pantalla principal (dashboard) t...

## Metadata
- **RF origen**: RF-131
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** ver en mi app móvil un dashboard con el conteo de espacios disponibles, la ocupación en tiempo real y los ingresos del día **para** tener visibilidad inmediata del estado de la sede sin abrir múltiples pantallas. ---

## Objetivo
La app móvil del operador debe mostrar en su pantalla principal (dashboard) tres datos clave actualizados en tiempo real: (1) total de espacios disponibles vs. total de espacios, (2) porcentaje de ocupación actual de la sede, y (3) total de ingresos acumulados del día en curso. Estos datos se actualizan automáticamente cada 30 segundos o ante un cambio significativo (entrada/salida/cierre de ticket). ---

## Comportamiento Específico

### Happy Path
1. Al abrir la app, el operador ve el dashboard principal de su sede asignada. 2. El sistema consulta occupancy-service para obtener el conteo de espacios disponibles y totales. 3. El sistema calcula el porcentaje de ocupación: `(ocupados / total) * 100`. 4. El sistema consulta payment-service para obtener los ingresos del día. 5. Los datos se muestran en tres tarjetas principales: Espacios, Ocupación, Ingresos. 6. Cada tarjeta es táctil y navega al detalle: - Espacios → Mapa de zonas con estados. - Ocupación → Lista de zonas con porcentajes. - Ingresos → Resumen de transacciones del día. 7. El indicador de última actualización se muestra en la parte inferior del dashboard. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | espacios_totales | Integer | Total de espacios configurados en la sede | | espacios_disponibles | Integer | Espacios actualmente sin vehículo | | espacios_ocupados | Integer | Espacios actualmente con vehículo | | porcentaje_ocupacion | Float | Porcentaje de ocupación (0.0 – 100.0) | | ingresos_dia | Decimal | Total de ingresos del día en moneda local | | cantidad_vehiculos_dia | Integer | Total de vehículos que ingresaron hoy | | tickets_abiertos | Integer | Cantidad de tickets actualmente abiertos | | ultimo_update | DateTime | Timestamp de la última actualización de datos | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | espacios_totales | Integer | Total de espacios configurados en la sede | | espacios_disponibles | Integer | Espacios actualmente sin vehículo | | espacios_ocupados | Integer | Espacios actualmente con vehículo | | porcentaje_ocupacion | Float | Porcentaje de ocupación (0.0 – 100.0) | | ingresos_dia | Decimal | Total de ingresos del día en moneda local | | cantidad_vehiculos_dia | Integer | Total de vehículos que ingresaron hoy | | tickets_abiertos | Integer | Cantidad de tickets actualmente abiertos | | ultimo_update | DateTime | Timestamp de la última actualización de datos | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Al abrir la app, el dashboard se carga en menos de 3 segundos. 2. El operador ve en todo momento el conteo de espacios disponibles actualizado. 3. El porcentaje de ocupación se calcula correctamente. 4. Los ingresos del día se muestran en la moneda configurada de la sede. 5. Los datos se actualizan automáticamente cada 30 segundos sin intervención del operador. 6. Si hay menos del 20% de espacios disponibles, el indicador cambia a rojo. 7. Cada tarjeta navega al detalle correspondiente al tocarla. 8. El dashboard funciona en modo offline mostrando datos en caché. ---

## Endpoints
- `GET /api/v1/operator/dashboard` — Retorna todos los datos del dashboard para la sede del operador - `GET /api/v1/operator/dashboard/spaces` — Detalle de espacios por zona - `GET /api/v1/operator/dashboard/revenue?date={date}` — Ingresos del día ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El dashboard es la pantalla principal al abrir la app; no requiere navegación adicional. - Se debe implementar un mecanismo de caché local para funcionar sin conexión temporal. - Los colores de indicador deben ser distinguibles para daltonismo (no solo rojo/verde, usar iconos también).
