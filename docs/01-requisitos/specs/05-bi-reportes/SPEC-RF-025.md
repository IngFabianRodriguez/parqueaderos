# SPEC-05-025 — Reportes Consolidados Multi-Sede

## Metadata
- **RF origen**: RF-025
- **Módulo**: 05-bi-reportes
- **Prioridad**: Alta
- **Servicios**: report-service, multi-tenant-service, billing-service

---

## User Story
**Como** operador con múltiples sedes **quiero** consultar reportes consolidados que agreguen datos de todas mis ubicaciones en una sola vista **para** comparar rendimiento entre sedes, identificar oportunidades de optimización y tener visibilidad global del negocio.

## Objetivo
El sistema debe permitir a operadores multi-sede consultar reportes consolidados que muestren KPIs agregados y desglosados por sede, incluyendo ingresos totales, ocupación consolidada, tiempo promedio de estadía por ubicación, y comparativas de rendimiento con métricas de desviación y ranking.

## Comportamiento Específico

### Happy Path
1. Usuario accede al módulo "Reportes Consolidados" desde el panel multi-sede
2. Sistema detecta las sedes autorizadas y las muestra como selector múltiple
3. Usuario selecciona una o más sedes (o "Todas") y define rango y tipo de reporte
4. Usuario hace clic en "Generar Reporte Consolidado"
5. Sistema verifica permisos en todas las sedes seleccionadas
6. Sistema lanza queries en paralelo a cada sede
7. Sistema agrega resultados y calcula métricas consolidadas
8. Sistema calcula ranking y desviación vs. promedio del grupo
9. Sistema renderiza tabla consolidada con drill-down colapsable por sede
10. Sistema renderiza gráficos comparativos

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Usuario con acceso a solo 1 sede | Error: "Requiere acceso a mínimo 2 sedes para reporte consolidado" |
| Una sede no tiene datos | Fila muestra valores en cero con "sin_datos: true", se excluye del ranking |
| Una sede tiene error de conexión | Advertencia en la sede; las demás se muestran; se ofrece retry parcial |
| Todas las sedes seleccionadas inactivas | Retorna 400: "Todas las sedes seleccionadas están inactivas" |
| Más de 20 sedes seleccionadas | Limita a 20 con advertencia |
| Comparativa con período sin datos en alguna sede | Columnas de variación muestran "N/A" |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_ids | array[UUID] | Lista de IDs de sedes a consolidar | Sí (min 2) |
| tipo_reporte | enum | 'ingresos', 'ocupacion', 'tiempo_promedio', 'mixto' | Sí |
| fecha_inicio | date | Inicio del rango | Sí |
| fecha_fin | date | Fin del rango | Sí |
| granularidad | enum | 'dia', 'semana', 'mes' | No (default: dia) |
| incluir_comparativa | boolean | Incluye período anterior | No (default: false) |
| ranking_por | enum | 'ingresos', 'ocupacion', 'tiempo_promedio' | No (default: ingresos) |
| formato_salida | enum | 'json', 'xlsx', 'csv' | No (default: json) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| fecha | date | Período de la fila |
| sede_id | UUID | Identificador de sede |
| sede_nombre | string | Nombre legible de la sede |
| ingreso_total | decimal | Ingresos del período |
| ocupacion_promedio | decimal | Tasa de ocupación promedio % |
| tiempo_promedio_min | decimal | Tiempo promedio en minutos |
| tickets_total | integer | Total tickets cerrados |
| ranking_ingresos | integer | Posición en ranking |
| desviacion_ingresos_% | decimal | % de desviación vs. promedio del grupo |
| meta_ingresos | decimal | Meta configurada (si existe) |
| cumplimiento_meta_% | decimal | % de cumplimiento de meta |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Usuario con acceso a 5 sedes puede generar reporte consolidado con ingresos, ocupación y tiempo promedio para las 5 sedes
2. El ingreso total consolidado se calcula como la suma de los ingresos de cada sede individual
3. El ranking de sedes se muestra correctamente sin duplicados (excepto en empates)
4. Las métricas de desviación muestran % de variación vs. promedio del grupo con 2 decimales
5. Drill-down abre el reporte individual (RF-023) sin pérdida de contexto
6. Exportación a XLSX genera una hoja de resumen consolidado y una hoja por cada sede
7. El sistema valida permisos en todas las sedes seleccionadas antes de ejecutar
8. Si una sede tiene meta de ingresos configurada, el reporte muestra % de cumplimiento

## Endpoints
- `POST /api/v1/reports/consolidated` — Genera reporte consolidado
- `GET /api/v1/reports/consolidated?{filtros}` — Versión GET
- `GET /api/v1/reports/consolidated/{sede_id}/drilldown` — Drill-down a reporte individual
- `GET /api/v1/reports/consolidated/summary` — Solo resumen consolidado

## Health Check
- `GET /health` → { "status": "ok" }