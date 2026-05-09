# SPEC-10-informes-125 — El sistema debe analizar los indicadores de productividad de cada operador y ...

## Metadata
- **RF origen**: RF-125
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** supervisor de operaciones **quiero** que el sistema detecte automáticamente operadores con indicadores anómalos (reembolsos excesivos, cierres sin pago) **para** investigar posibles fraudes o errores operativos de forma oportuna. ---

## Objetivo
El sistema debe analizar los indicadores de productividad de cada operador y detectar anomalías comparando contra umbrales configurables y patrones históricos. Se deben identificar al menos dos tipos de anomalías: (1) tasa de reembolsos superior al umbral definido, y (2) transacciones cerradas sin cobro asociado. Cuando se detecte una anomalía, se generará una notificación al supervisor configurado. ---

## Comportamiento Específico

### Happy Path
1. El sistema ejecuta el análisis de anomalías de forma periódica (por defecto: cada hora) o a demanda via API. 2. Para cada operador con actividad en el período (últimas 24 horas por defecto): a. **Anomalía tipo A — Reembolsos excesivos**: Calcula `tasa_reembolso = reembolsos / transacciones_cerradas`. Si `tasa_reembolso > umbral_reembolso` (default: 5%), marca como anomalía. b. **Anomalía tipo B — Cierres sin pago**: Calcula `tasa_cierre_sin_pago = cierres_sin_pago / transacciones_cerradas`. Si `tasa_cierre_sin_pago > umbral_cierre_sin_pago` (default: 3%), marca como anomalía. c. **Anomalía tipo C — Operaciones manuales excesivas**: Calcula `ratio_manual = aperturas_manuales / transacciones_abiertas`. Si `ratio_manual > umbral_manual` (default: 10%), marca como anomalía. 3. Por cada anomalía detectada: - Se crea un registro en `anomaly_log` con operador, tipo, valores, umbral excedido y timestamp. - Se envía notificación al supervisor configurado para la sede. 4. Los resultados se presentan en el dashboard de reportes bajo la categoría "Anomalías de Operador". ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | operador_id | UUID | Identificador del operador | | operador_nombre | String | Nombre completo del operador | | tipo_anomalia | Enum | Tipo de anomalía: REEMBOLSO_EXCESIVO, CIERRE_SIN_PAGO, APERTURA_MANUAL_EXCESIVA | | valor_actual | Decimal | Valor actual del indicador | | umbral_configurado | Decimal | Umbral que fue excedido | | tasa | Decimal | Porcentaje calculado (reembolsos/transacciones) | | gravedad | Enum | ALTA, MEDIA, BAJA según configuración | | fecha_deteccion | DateTime | Timestamp de la detección | | transacciones_evaluadas | Integer | Total de transacciones consideradas | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | operador_id | UUID | Identificador del operador | | operador_nombre | String | Nombre completo del operador | | tipo_anomalia | Enum | Tipo de anomalía: REEMBOLSO_EXCESIVO, CIERRE_SIN_PAGO, APERTURA_MANUAL_EXCESIVA | | valor_actual | Decimal | Valor actual del indicador | | umbral_configurado | Decimal | Umbral que fue excedido | | tasa | Decimal | Porcentaje calculado (reembolsos/transacciones) | | gravedad | Enum | ALTA, MEDIA, BAJA según configuración | | fecha_deteccion | DateTime | Timestamp de la detección | | transacciones_evaluadas | Integer | Total de transacciones consideradas | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El sistema detecta operators cuya tasa de reembolso supere el umbral configurable. 2. El sistema detecta operators con cierres de transacción sin pago asociado que superen el umbral. 3. Las anomalías detectadas se presentan en un reporte dedicado con filtrado por sede, operador y tipo. 4. Se genera notificación por email al supervisor por cada anomalía detectada (fallas de notificación no bloquean el proceso). 5. Los logs de anomalías persisten durante al menos 90 días. 6. Los umbrales son configurables por sede y por tipo de anomalía. 7. Un operador puede aparecer múltiples veces en el reporte si tiene más de un tipo de anomalía. ---

## Endpoints
- `GET /api/v1/reports/anomalies/operator` — Consulta anomalías detectadas - `POST /api/v1/reports/anomalies/run` — Ejecuta análisis de anomalías a demanda - `PUT /api/v1/reports/anomalies/thresholds` — Actualiza umbrales de anomalía ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los umbrales por defecto (5% reembolsos, 3% cierres sin pago, 10% manuales) pueden ajustarse por sede vía API de configuración. - La gravedad de la anomalía se determina por combinación de tipo y magnitud del desvío: si el valor es >2x el umbral → ALTA, entre 1.5x y 2x → MEDIA, menor a 1.5x → BAJA. - El análisis de anomalías corre como job programado por defecto cada hora; puede also ser invoked manualmente via endpoint. - Los operadores dados de baja no se incluyen en el análisis activo, pero sus anomalías históricas persisten en el log.
