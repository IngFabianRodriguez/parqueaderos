# SPEC-10-informes-122 — El sistema debe generar un reporte de clientes con deuda pendiente

## Metadata
- **RF origen**: RF-122
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin o sede_admin **quiero** consultar un reporte de morosos **para** saber qué clientes tienen deuda pendiente, cuánto deben, cuánto tiempo llevan sin pagar y cuántas veces hemos intentado contactarlos. ---

## Objetivo
El sistema debe generar un reporte de clientes con deuda pendiente. Por cada moroso se debe mostrar: identificación del cliente, monto total adeudado, antigüedad de la deuda (días desde el vencimiento), cantidad de intentos de contacto registrados, y el estado de la cuenta. ---

## Comportamiento Específico

### Happy Path
1. El usuario solicita el reporte de morosos con filtros (RF-117): sede, rango de fechas (opcionalmente para antigüedad) 2. El `reporting-service` consulta `billing-service` para obtener cuentas con estado `overdue` 3. Por cada cuenta morosa: a. Obtiene datos del cliente (`cliente_id`, nombre, identificación) b. Suma todos los cargos vencidos para obtener `monto_total_deuda` c. Calcula `antigüedad_dias = HOY - fecha_vencimiento_más_antigua` d. Cuenta intentos de contacto en `contact_log` para ese cliente e. Obtiene `último_contacto` más reciente 4. Calcula totales: suma de todas las deudas, cantidad de morosos 5. Ordena por `monto_total_deuda` descendente (default) o por `antigüedad` si se pide 6. Retorna el reporte ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | morosos | array | Lista de clientes morosos | | morosos[].cliente_id | uuid | Identificador del cliente | | morosos[].nombre | string | Nombre completo o razón social | | morosos[].identificacion | string | DUI/NIT/RUC según país | | morosos[].sede_id | uuid | Sede donde ocurrió la deuda | | morosos[].sede_nombre | string | Nombre de la sede | | morosos[].monto_total_deuda | decimal | Suma de todos los cargos vencidos | | morosos[].antiguedad_dias | integer | Días desde el vencimiento más antiguo | | morosos[].fecha_vencimiento | date | Fecha del cargo más antiguo vencido | | morosos[].intentos_contacto | integer | Cantidad de veces que se intentó contactar | | morosos[].ultimo_contacto | datetime | Fecha y hora del último intento | | morosos[].telefono | string | Teléfono registrado del cliente | | morosos[].email | string | Email registrado del cliente | | totales | object | Agregados del reporte | | totales.cantidad_morosos | integer | Total de clientes en el reporte | | totales.monto_total_deuda | decimal | Suma de todas las deudas | | totales.deuda_promedio | decimal | Monto promedio por moroso | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | morosos | array | Lista de clientes morosos | | morosos[].cliente_id | uuid | Identificador del cliente | | morosos[].nombre | string | Nombre completo o razón social | | morosos[].identificacion | string | DUI/NIT/RUC según país | | morosos[].sede_id | uuid | Sede donde ocurrió la deuda | | morosos[].sede_nombre | string | Nombre de la sede | | morosos[].monto_total_deuda | decimal | Suma de todos los cargos vencidos | | morosos[].antiguedad_dias | integer | Días desde el vencimiento más antiguo | | morosos[].fecha_vencimiento | date | Fecha del cargo más antiguo vencido | | morosos[].intentos_contacto | integer | Cantidad de veces que se intentó contactar | | morosos[].ultimo_contacto | datetime | Fecha y hora del último intento | | morosos[].telefono | string | Teléfono registrado del cliente | | morosos[].email | string | Email registrado del cliente | | totales | object | Agregados del reporte | | totales.cantidad_morosos | integer | Total de clientes en el reporte | | totales.monto_total_deuda | decimal | Suma de todas las deudas | | totales.deuda_promedio | decimal | Monto promedio por moroso | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `monto_total_deuda` es la suma exacta de todos los cargos con estado `overdue` del cliente 2. La `antiguedad_dias` se calcula respecto al cargo más antiguo vencido, no al más reciente 3. El reporte se genera en menos de 10 segundos para hasta 10,000 morosos 4. Se puede exportar según RF-128 5. Si un cliente tiene contacto exitoso después de ser reportado como moroso, el `intentos_contacto` sigue contando (no se reinicia) ---

## Endpoints
- `GET /api/v1/reports/debtors` — Genera reporte de morosos - `GET /api/v1/billing/accounts?status=overdue` — Consulta de cuentas vencidas ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Este reporte es sensible (datos personales y financieros); se debe registrar el acceso en audit log - Los intentos de contacto se incrementan automáticamente cuando se usa la funcionalidad de contacto del sistema (RF relacionado: gestión de cobros) - Se recomienda que la UI muestre los morosos con deuda > 30 días en color rojo para fácil identificación
