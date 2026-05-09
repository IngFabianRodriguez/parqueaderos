# SPEC-15-soporte-180 — Proporcionar al administrador del tenant (owner de la empresa de parqueo) un ...

## Metadata
- **RF origen**: RF-180
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin **quiero** ver el NPS y la calificación promedio de cada sede **para** identificar problemas de servicio, evaluar el desempeño de mis operadores y tomar decisiones basadas en datos. ---

## Objetivo
Proporcionar al administrador del tenant (owner de la empresa de parqueo) un dashboard con métricas de satisfacción del cliente: NPS global, NPS por sede, calificación promedio por sede, tendencia temporal de calificaciones, y distribución de respuestas. Todo esto segmentado por sede, período y opcionalmente por operador asignado. ---

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a sección "Satisfacción / Feedback" desde su panel de administración 2. Sistema muestra dashboard con vista general de NPS y calificaciones por sede 3. Dashboard incluye: - **NPS Global**: Puntuación NPS calculada (-100 a +100) conbenchmark del sector - **NPS por Sede**: Lista de sedes ordenadas por NPS (mejor a peor) - **Calificación Promedio**: Barra de 1-5 estrellas por sede con historial semanal - **Distribución de Respuestas**: Gráfico de cómo se distribuyen las calificaciones (1-5 estrellas) - **Tendencia Temporal**: Gráfico de línea mostrando evolución de NPS y calificación en los últimos 30/60/90 días - **Feedbacks Recientes**: Lista de últimos 20 comentarios con calificaciones bajas (1-2 estrellas) para revisión 4. Admin puede filtrar dashboard por: - Período: última semana, último mes, últimos 3 meses, último año, personalizado - Sede: todas o una específica - Operador: todos o filtrar por operador específico (si tracking de operador implementado) 5. Admin puede exportar reporte en formatos: CSV, Excel, PDF 6. Click en una sede específica drill down para ver: - Detalle de calificaciones por día - Lista completa de feedbacks con comentarios - Comparación con otras sedes del mismo plan/región 7. Sistema genera alertas automáticas cuando: - NPS de una sede cae por debajo de 0 (detractor neto) - Calificación promedio cae por debajo de 3 estrellas - Hay un incremento > 20% en feedbacks negativos vs período anterior ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Dashboard carga en menos de 3 segundos con datos de los últimos 30 días 2. NPS se calcula correctamente según fórmula estándar: %Promotores - %Detractores 3. Admin puede filtrar por cualquier sede y período disponible sin errores 4. Datos exportados en CSV contain todas las métricas con datos detallados por respuesta 5. Alertas de NPS bajo se generan y envian por email al tenant admin dentro de 1 hora de detectado 6. Drill-down a sede muestra datos específicos de esa sede en menos de 1 segundo 7. Comparación de tendencias muestra al menos 90 días de historial ---

## Endpoints
- `GET /api/v1/analytics/nps/dashboard?from={date}&to={date}&sede_id={id}` — Dashboard NPS global y por sede - `GET /api/v1/analytics/nps/sedes/{sede_id}/detalle?from={date}&to={date}` — Drill-down por sede - `GET /api/v1/analytics/feedbacks/negativos?limit={n}` — Lista de feedbacks negativos recientes - `GET /api/v1/analytics/nps/export?formato=csv|xlsx|pdf` — Exportación de reporte ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- **Cálculo del NPS**: Se pregunta al cliente "¿Qué tan probable es que recomiende este parqueadero a un amigo?" (escala 0-10). Promotores=9-10, Pasivos=7-8, Detractores=0-6. NPS = %Promotores - %Detractores - **Benchmark sectorial**: Usar datos públicos de NPS promedio de industria de movilidad/estacionamiento (~35) como referencia - **Frecuencia de actualización**: Dashboard se actualiza cada 1 hora con datos nuevos;有能力 para refresh manual - **Retención de datos**: Datos de feedback se mantienen por 2 años para análisis históricos - **Segmentación por operador**: Si se implementa tracking de operador (ver notas de RF-176), incluir calificación de desempeño por operador - **Alertas proactivas**: Sistema debe enviar email semanal resumiendo NPS y需要注意 sedes al tenant admin
