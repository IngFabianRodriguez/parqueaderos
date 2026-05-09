# SPEC-05-023 — Generación de Reportes de Ingresos, Ocupación y Tiempo Promedio de Estadía

## Metadata
- **RF origen**: RF-023
- **Módulo**: 05-bi-reportes
- **Prioridad**: Alta
- **Servicios**: report-service, billing-service, occupancy-service

---

## User Story
**Como** operador de parqueo **quiero** consultar reportes de ingresos, ocupación y tiempo promedio de estadía **para** tomar decisiones informadas sobre precios, capacidad y operación diaria.

## Objetivo
El sistema debe permitir generar reportes operativos en formato tabular y gráfico que muestren: (1) ingresos por período, (2) tasa de ocupación por sede y por hora, y (3) tiempo promedio de estadía por tipo de vehículo. Los reportes deben ser consultables en línea y exportables, con datos actualizados en tiempo real o con delta máximo de 15 minutos.

## Comportamiento Específico

### Happy Path
1. Operador accede al módulo "Reportes" desde el panel de administración
2. Sistema presenta formulario con filtros: sede, tipo de reporte, rango de fechas, granularidad
3. Operador selecciona filtros y hace clic en "Generar Reporte"
4. Sistema valida que el rango no supere 90 días corridos
5. Sistema consulta agregaciones según filtros
6. Sistema renderiza tabla con totales y subtotales
7. Sistema renderiza gráfico de líneas/barras según tipo
8. Operador puede exportar (RF-024)
9. Sistema registra generación en auditoría

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Rango > 90 días | Sistema rechaza: "El rango máximo es 90 días" |
| Sede sin transacciones | Reporte muestra todos los campos en cero con leyenda "Sin datos" |
| Usuario sin permisos en sede | Retorna 403 Forbidden |
| Base de datos no disponible | Retorna 503 con retry-after de 30s |
| Ticket sin egreso (abierto) | Se excluye del cálculo de tiempo promedio; se incluye en ocupación |
| Concurrencia > 100 solicitudes/min | Cola de procesamiento; 429 si se excede |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| tipo_reporte | enum | 'ingresos', 'ocupacion', 'tiempo_promedio' | Sí |
| fecha_inicio | datetime | Inicio del rango (inclusive) | Sí |
| fecha_fin | datetime | Fin del rango (inclusive) | Sí |
| granularidad | enum | 'hora', 'dia', 'semana', 'mes' | No (default: dia) |
| tipo_vehiculo | string | Filtrar por categoría de vehículo | No |
| exportar | boolean | Si true, genera archivo descargable | No |

## Datos de Salida
### Reporte de Ingresos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| periodo | datetime | Período agregado |
| total_ingresos | decimal | Suma de pagos recibidos |
| total_transacciones | integer | Cantidad de transacciones completadas |
| total_tickets | integer | Cantidad de tickets cerrados |
| promedio_por_ticket | decimal | Ingreso promedio por ticket |
| moneda | string | ISO 4217 del monto |

### Reporte de Ocupación
| Campo | Tipo | Descripción |
|-------|------|-------------|
| hora | datetime | Hora de la medición |
| espacios_totales | integer | Capacidad total |
| espacios_ocupados | integer | Espacios con estado 'ocupado' |
| tasa_ocupacion | decimal | Porcentaje (0-100) |
| tickets_ativos | integer | Tickets abiertos |

### Reporte de Tiempo Promedio
| Campo | Tipo | Descripción |
|-------|------|-------------|
| periodo | datetime | Período agregado |
| tiempo_promedio_minutos | decimal | Duración media |
| tiempo_mediana_minutos | decimal | Mediana de duración |
| tiempo_p90_minutos | decimal | Percentil 90 |
| total_tickets | integer | Cantidad de tickets cerrados |
| conteo_por_tipo | JSON | Desglose por tipo de vehículo |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Operador puede generar reporte de ingresos para una sede en rango ≤ 90 días y se despliega en < 5s para rangos ≤ 30 días
2. Reporte de ingresos muestra correctamente la suma de montos diferenciando por estado (pagado, pendiente, reembolsado)
3. Reporte de ocupación muestra datos con latencia máxima de 15 minutos
4. Tiempo promedio se calcula solo con tickets cerrados (con egreso) y excluye outliers > 24h
5. Reportes incluyen breakdown por tipo de vehículo cuando el filtro está activo
6. Cada generación de reporte se registra en log de auditoría con usuario, timestamp, filtros y tamaño
7. Usuario sin rol adecuado recibe 403 al acceder al módulo

## Endpoints
- `GET /api/v1/reports/ingresos?sede_id={uuid}&fecha_inicio={date}&fecha_fin={date}`
- `GET /api/v1/reports/ocupacion?sede_id={uuid}&fecha={date}&realtime={bool}`
- `GET /api/v1/reports/tiempo-promedio?sede_id={uuid}&fecha_inicio={date}&fecha_fin={date}&tipo_vehiculo={string}`
- `POST /api/v1/reports/async` — Cola generación asíncrona para reportes > 30 días

## Health Check
- `GET /health` → { "status": "ok" }