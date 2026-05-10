# SPEC-07-075 — Dashboard BI con Tendencias en Tiempo Real (Enterprise+)

## Metadata
- **RF origen**: RF-075
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: analytics-service, bi-service, site-service

---

## User Story
**Como** administrador de un tenant Enterprise **quiero** ver un dashboard con tendencias de ocupación, ingresos y transacciones en tiempo real **para** tomar decisiones operativas basadas en datos actualizados al minuto.

## Objetivo
El sistema debe exponer un dashboard BI que muestre métricas clave en tiempo real: ocupación actual y trends, ingresos del día/mes, volumen de transacciones. Los datos se actualizan automáticamente cada 60 segundos. Disponible únicamente para tenants Enterprise+.

## Comportamiento Específico

### Carga del dashboard
1. El usuario accede a `GET /dashboard/bi` desde el admin panel.
2. El sistema verifica: plan del tenant es Enterprise+; usuario tiene rol con acceso a BI.
3. El sistema consulta datos del período por defecto (hoy): ocupación en tiempo real, ingresos del día, transacciones del día.
4. Se renderiza el dashboard con los datos cargados.
5. Cada 60 segundos, el frontend hace `GET /api/v1/analytics/realtime-summary` y actualiza widgets.

### Widgets del Dashboard
- Ocupación en tiempo real (% de espacios ocupados vs total).
- Tendencia de ocupación (24h) — gráfico de línea.
- Ingresos del día — tarjeta con monto y variación vs ayer.
- Ingresos por sede — gráfico de barras.
- Transacciones por hora — gráfico de línea.
- Tiempo promedio de permanencia.
- Ingresos del mes — tarjeta con progreso vs meta.
- Top 5 espacios con mayor rotación.

### Filtros disponibles
- Rango de fechas: Hoy, Ayer, últimos 7 días, último mes, mes actual, personalizado.
- Sede: Todas o específica.
- Zona: Todas o específica.
- Granularidad: Hora, Día, Semana, Mes.

## Criterios de Aceptación
1. El dashboard carga en < 3 segundos con datos del día actual.
2. Los widgets se actualizan automáticamente cada 60 segundos.
3. El usuario puede filtrar por sede, zona, rango de fechas y granularidad.
4. Los datos históricos tienen resolución de 1 hora para rangos hasta 30 días, y 1 día para rangos mayores.
5. El acceso está restringido a tenants Enterprise+ y roles con permisos de BI.
6. Todos los valores monetarios se muestran en la moneda del tenant.
7. Las tendencias muestran comparison vs período anterior.

## Datos de Entrada
- **tenant_id** — ID del tenant (UUID, required, extraído de sesión)
- **date_range** — Rango de fechas: `today`, `yesterday`, `last_7_days`, `last_month`, `current_month`, `custom` (enum, default: `today`)
- **start_date** — Fecha inicio para rango personalizado (ISO date, conditional)
- **end_date** — Fecha fin para rango personalizado (ISO date, conditional)
- **site_id** — Filtrar por sede específica (UUID, optional, null = todas)
- **zone_id** — Filtrar por zona específica (UUID, optional)
- **granularity** — Granularidad de datos: `hour`, `day`, `week`, `month` (enum, default: `day`)

## Datos de Salida
- **widgets** — Objeto con datos de cada widget del dashboard:
  - `realtime_occupancy` — Porcentaje de ocupación actual y total de espacios
  - `occupancy_trend` — Array de datos de ocupación últimas 24h (timestamp, percentage)
  - `daily_revenue` — Ingresos del día y variación vs ayer (amount, variation_percentage)
  - `revenue_by_site** — Array de ingresos por sede (site_id, site_name, amount)
  - `transactions_per_hour** — Array de transacciones por hora (hour, count)
  - `avg_stay_time** — Tiempo promedio de permanencia en minutos (number)
  - `monthly_revenue** — Ingresos del mes y progreso vs meta (amount, progress_percentage)
  - `top_spaces** — Top 5 espacios con mayor rotación (space_id, entries, revenue)
- **filters_applied** — Objeto con los filtros utilizados
- **last_updated** — Timestamp de última actualización de datos (ISO datetime)