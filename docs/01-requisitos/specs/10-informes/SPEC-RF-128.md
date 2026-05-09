# SPEC-10-informes-128 — El sistema debe permitir que cualquier reporte generado en el módulo de infor...

## Metadata
- **RF origen**: RF-128
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede **quiero** exportar cualquier reporte a Excel, CSV o PDF **para** poder compartir la información con stakeholders, archivarla o analizarla en herramientas externas. ---

## Objetivo
El sistema debe permitir que cualquier reporte generado en el módulo de informes pueda ser exportado en formato Excel (.xlsx), CSV y PDF. La exportación debe mantener la estructura y datos del reporte tal como se visualiza en pantalla, incluyendo headers, totales y formateo. ---

## Comportamiento Específico

### Happy Path
1. El usuario visualiza un reporte en el módulo de informes. 2. El usuario hace clic en el botón "Exportar" y selecciona el formato (XLSX, CSV o PDF). 3. El sistema valida que el usuario tenga permisos de exportación. 4. El sistema prepara la data del reporte: - **XLSX**: Genera workbook con sheets, aplica estilo a headers (negrita, color de fondo), columnas auto-ajustadas, formulas de suma para totales. - **CSV**: Genera archivo delimitado por comas, encoding UTF-8, sin fórmulas ni estilos. - **PDF**: Genera documento con layout de tabla, headers en cada página, pies de página con número de página y fecha de generación. 5. El sistema retorna el archivo para descarga o lo almacena temporalmente para link de descarga. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | archivo_descarga | Binary | Archivo en el formato seleccionado | | nombre_archivo | String | Nombre sugerido: `{reporte_nombre}_{YYYYMMDD_HHmmss}.{ext}` | | tamano_bytes | Integer | Tamaño del archivo en bytes | | tipo_contenido | String | MIME type: application/vnd.openxmlformats..., text/csv, application/pdf | | filas_incluidas | Integer | Cantidad de filas incluidas en el archivo | | url_temporal | String | URL temporal de descarga (validez 24h) si se almacenó | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | archivo_descarga | Binary | Archivo en el formato seleccionado | | nombre_archivo | String | Nombre sugerido: `{reporte_nombre}_{YYYYMMDD_HHmmss}.{ext}` | | tamano_bytes | Integer | Tamaño del archivo en bytes | | tipo_contenido | String | MIME type: application/vnd.openxmlformats..., text/csv, application/pdf | | filas_incluidas | Integer | Cantidad de filas incluidas en el archivo | | url_temporal | String | URL temporal de descarga (validez 24h) si se almacenó | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Cualquier reporte del módulo puede exportarse en los tres formatos: XLSX, CSV y PDF. 2. Los datos exportados coinciden exactamente con los datos visibles en pantalla en el momento de la exportación. 3. El archivo XLSX es abrible en Microsoft Excel sin errores de formato o fórmulas. 4. El archivo CSV es abrible en cualquier editor de texto o herramienta de hojas de cálculo. 5. El archivo PDF mantiene legibilidad y se puede imprimir correctamente en tamaño A4. 6. La exportación de un reporte de hasta 10,000 filas no toma más de 10 segundos. 7. Los archivos exportados incluyen timestamp de generación en el nombre. 8. Archivos temporal de descarga expiran después de 24 horas. ---

## Endpoints
- `POST /api/v1/reports/{reporte_id}/export` — Genera la exportación en el formato solicitado - `GET /api/v1/reports/exports/{export_id}/download` — Descarga un archivo de exportación previamente generado ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La exportación en PDF utiliza una biblioteca de rendering que soportael estándar PDF/A para archivo. - Para reportes muy grandes, se recomienda usar CSV que es más rápido de generar. - Los archivos exportados no se almacenan permanentemente en el servidor; solo se mantienen como descarga temporal (24h) o se envían directamente. - Si el usuario tiene configuración regional diferente, los separadores de decimales y miles se ajustan al formato de la región del tenant.
