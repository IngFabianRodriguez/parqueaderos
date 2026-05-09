# SPEC-10-informes-118 — El sistema debe calcular y mostrar automáticamente, junto a cualquier reporte...

## Metadata
- **RF origen**: RF-118
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin **quiero** ver la comparativa automática entre el período seleccionado y el período anterior **para** identificar tendencias de crecimiento o Decline en ingresos, ocupación y productividad. ---

## Objetivo
El sistema debe calcular y mostrar automáticamente, junto a cualquier reporte que Involucre un rango de fechas, la comparación con el período inmediatamente anterior de igual duración. Se debe mostrar la variación absoluta y el porcentaje de variación (%) con respecto al período anterior. ---

## Comportamiento Específico

### Happy Path
1. El usuario ejecuta cualquier reporte con un rango de fechas (RF-117) 2. El `reporting-service` recibe `fecha_inicio` y `fecha_fin` 3. Calcula `periodo_actual`: desde `fecha_inicio` hasta `fecha_fin` 4. Calcula `periodo_anterior`: la misma duración en días inmediatamente antes - `diff_dias = fecha_fin - fecha_inicio` - `periodo_anterior_inicio = fecha_inicio - diff_dias` - `periodo_anterior_fin = fecha_inicio - 1 día` 5. Ejecuta la consulta del reporte para `periodo_actual` 6. Ejecuta la misma consulta para `periodo_anterior` 7. Calcula: `variacion_absoluta = valor_actual - valor_anterior` 8. Calcula: `variacion_porcentual = ((valor_actual - valor_anterior) / valor_anterior) * 100` (si valor_anterior ≠ 0) 9. Retorna ambos períodos con la comparativa ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | periodo_actual | object | Datos del período seleccionado | | periodo_anterior | object | Datos del período anterior de igual duración | | comparativa | object | Objeto con variación absoluta y porcentual | | comparativa.variacion_absoluta | decimal | Diferencia (actual - anterior) | | comparativa.variacion_porcentual | decimal | Porcentaje de cambio (puede ser negativo) | | comparativa.tendencia | enum | `up` (aumento), `down` (disminución), `stable` (< 1% cambio), `no_data` | | dias_comparados | integer | Cantidad de días de cada período | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | periodo_actual | object | Datos del período seleccionado | | periodo_anterior | object | Datos del período anterior de igual duración | | comparativa | object | Objeto con variación absoluta y porcentual | | comparativa.variacion_absoluta | decimal | Diferencia (actual - anterior) | | comparativa.variacion_porcentual | decimal | Porcentaje de cambio (puede ser negativo) | | comparativa.tendencia | enum | `up` (aumento), `down` (disminución), `stable` (< 1% cambio), `no_data` | | dias_comparados | integer | Cantidad de días de cada período | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Si el usuario selecciona mayo (31 días), el período anterior debe ser los 31 días previos (30 de abril hacia atrás) 2. La `variacion_porcentual` se calcula con 2 decimales de precisión 3. La comparativa se muestra en todo reporte que use el filtro de fechas (RF-117) 4. Si `valor_anterior = 0` y `valor_actual > 0`, la variación porcentual se muestra como "+∞%" o "N/A" 5. La tendencia se clasifica automáticamente: `up` si > +1%, `down` si < -1%, `stable` en otro caso ---

## Endpoints
- `GET /api/v1/reports/income` — Con `include_comparison=true` retorna la comparativa - `GET /api/v1/reports/occupancy` — Con `include_comparison=true` retorna la comparativa - `GET /api/v1/reports/{report_type}?include_comparison=true` — Parámetro genérico ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La comparativa es paramétrica: se activa con `include_comparison=true` en la query - Para reportes que no Involucren valores numéricos (ej: reportes de estado), la comparativa puede no ser applicable y se omite - El rango de fechas del período anterior se muestra en la UI para transparencia del usuario - Se recomienda que la UI muestre flechas de color (verde ↑, rojo ↓) para facilitar lectura rápida
