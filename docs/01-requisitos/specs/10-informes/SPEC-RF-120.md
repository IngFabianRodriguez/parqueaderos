# SPEC-10-informes-120 — El sistema debe generar una visualización tipo heatmap que muestre la tasa de...

## Metadata
- **RF origen**: RF-120
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sede_admin o tenant_admin **quiero** ver un heatmap (gráfico de calor) de ocupación que combine día de la semana con hora del día **para** identificar visualmente los horarios y días de mayor y menor demanda. ---

## Objetivo
El sistema debe generar una visualización tipo heatmap que muestre la tasa de ocupación promedio para cada combinación de día de la semana (lunes a domingo, 7 columnas) y hora del día (0-23, 24 filas). Cada celda representa el promedio de la tasa de ocupación para ese horario específico en el período seleccionado. Los colores deben variar de frío (baja ocupación) a caliente (alta ocupación). ---

## Comportamiento Específico

### Happy Path
1. El usuario solicita el heatmap con filtros (RF-117): sede, rango de fechas 2. El `reporting-service` obtiene `total_espacios` de la sede 3. Para cada día de la semana d (0=Domingo a 6=Sábado) y cada hora h (0-23): a. Filtra transacciones donde `DAYOFWEEK(fecha) = d` y `hora_entrada <= h < hora_salida` b. Calcula `tasa_promedio = AVG(ocupados / total_espacios * 100)` para esa combinación 4. Construye la matriz 7×24 con los promedios 5. Normaliza la escala de colores: el valor mínimo de toda la matriz = color frío, máximo = color calor 6. Retorna la matriz de datos y la escala de normalización para que la UI renderice el heatmap ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | dias_semana | array | Lista ordenada ["Domingo","Lunes",...,"Sábado"] | | matriz | array | Matriz 7×24 de objetos: `{ dia, hora, tasa_ocupacion_promedio, color_hex }` | | escala | object | `{ min: decimal, max: decimal, mid: decimal }` para normalización de color | | valores_por_dia | array | Promedio por día de la semana (para label de columna) | | valores_por_hora | array | Promedio por hora del día (para label de fila) | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | sede_nombre | string | Nombre de la sede | | dias_semana | array | Lista ordenada ["Domingo","Lunes",...,"Sábado"] | | matriz | array | Matriz 7×24 de objetos: `{ dia, hora, tasa_ocupacion_promedio, color_hex }` | | escala | object | `{ min: decimal, max: decimal, mid: decimal }` para normalización de color | | valores_por_dia | array | Promedio por día de la semana (para label de columna) | | valores_por_hora | array | Promedio por hora del día (para label de fila) | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La matriz siempre tiene exactamente 7 columnas (días) × 24 filas (horas) 2. Los colores se normalizan en el rango [min, max] de la matriz para máxima legibilidad 3. El heatmap incluye tooltips que muestran la tasa exacta al hacer hover 4. Se puede superponer la misma sede en períodos diferentes (comparar mes a mes) si se solicita con `include_comparison=true` 5. El tiempo de generación del heatmap es < 15 segundos para 1 año de datos ---

## Endpoints
- `GET /api/v1/reports/occupancy/heatmap` — Genera datos del heatmap - `GET /api/v1/reports/occupancy/hourly` — Puede ser usado como fuente de datos ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El heatmap se renderiza principalmente en el frontend; el backend solo provee los datos y la escala de color - Se recomienda usar una paleta de colores accesible (no solo rojo/verde para daltonismo) - La celda con valor máximo debe tener color "caliente" (rojo/oscuro) y la mínima "frío" (azul/claro) - Para tenants con múltiples sedes, se puede generar un heatmap consolidado promediando las tasas de ocupación
