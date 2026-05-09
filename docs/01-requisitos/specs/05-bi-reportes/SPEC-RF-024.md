# SPEC-05-024 — Exportación de Datos a Excel/CSV y Conectores BI

## Metadata
- **RF origen**: RF-024
- **Módulo**: 05-bi-reportes
- **Prioridad**: Media
- **Servicios**: report-service, export-service, api-gateway

---

## User Story
**Como** analista de negocio **quiero** exportar los datos de reportes a Excel y CSV, y conectar herramientas de BI como Power BI y Google Data Studio **para** realizar análisis avanzados y compartir dashboards con stakeholders.

## Objetivo
El sistema debe proporcionar mecanismos de exportación en formatos estructurados (XLSX, CSV) y exponer endpoints API compatibles con herramientas de visualización BI (Power BI, Google Data Studio) mediante soporte para OData y JSON bidireccional.

## Comportamiento Específico

### Happy Path
1. Usuario genera un reporte (RF-023) y visualiza resultados
2. Usuario hace clic en "Exportar" y selecciona formato (XLSX o CSV)
3. Sistema valida que el volumen no exceda 50,000 registros para exportación sincrónica
4. Sistema genera archivo con los mismos filtros del reporte
5. Sistema retorna archivo descargable con nombre: `{tipo_reporte}_{sede}_{fecha_inicio}_{fecha_fin}.{ext}`
6. Sistema registra la exportación en auditoría

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Exportación > 50,000 registros sincrónica | Sistema rechaza: "Exporte más de 50k registros de forma asíncrona" |
| Exportación async > 500,000 registros | Sistema rechaza: "Volumen máximo: 500k registros" |
| Token OAuth2 expirado durante consumo BI | Retorna 401 con header WWW-Authenticate; la herramienta debe re-autenticar |
| Rate limit en consumo BI (> 100 req/min) | Retorna 429 con Retry-After |
| Formato CSV con caracteres especiales | Encoding UTF-8 con BOM para compatibilidad Excel |
| Vacío en rango de fechas | Archivo generado con headers pero 0 filas + leyenda "Sin datos" |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| reporte_tipo | enum | 'ingresos', 'ocupacion', 'tiempo_promedio' | Sí |
| sede_id | UUID | Identificador de la sede | Sí |
| fecha_inicio | date | Inicio del rango | Sí |
| fecha_fin | date | Fin del rango | Sí |
| formato | enum | 'xlsx', 'csv' | Sí |
| async | boolean | Si true, genera en background | No (default: false) |
| incluir_detalle | boolean | Si true, incluye filas detalle | No (default: false) |
| tipo_vehiculo | string | Filtrar por tipo | No |
| granularidad | enum | 'hora', 'dia', 'semana', 'mes' | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| archivo | binary | Archivo descargable |
| nombre_archivo | string | Nombre formateado con metadatos |
| mime_type | string | 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' o 'text/csv' |
| registros | integer | Cantidad de filas generadas |
| generacion_timestamp | datetime | Cuándo se generó |
| url_expiracion | string | URL con TTL de 24h para descargas async |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Usuario puede exportar reporte de ingresos a XLSX y el archivo se abre correctamente en Microsoft Excel
2. Usuario puede exportar a CSV con encoding UTF-8 y se abre correctamente en Google Sheets
3. Power BI puede conectarse vía OData y listar los EntitySets disponibles
4. Power BI aplica row-level security por sede según los scopes del token OAuth2
5. Google Data Studio puede consumir endpoints JSON y mapear campos correctamente
6. Exportaciones de más de 50k registros se procesan de forma asíncrona y completan en < 5 min
7. Cada exportación genera registro en auditoría con usuario, formato, cantidad de registros y hash de integridad
8. Archivos exportados incluyen suma de verificación (SHA256)

## Endpoints
- `POST /api/v1/exports` — Crear exportación sincrónica o encolar async
- `GET /api/v1/exports/{job_id}` — Consultar estado de job async
- `GET /api/v1/exports/{job_id}/download` — Descargar archivo generado
- `GET /api/v1/exports/catalog` — Listar templates de exportación predefinidos
- `GET /odata/v1/transactions` — Endpoint OData para Power BI
- `GET /api/v1/bi/reports/{tipo}` — Endpoint JSON para herramientas REST

## Health Check
- `GET /health` → { "status": "ok" }