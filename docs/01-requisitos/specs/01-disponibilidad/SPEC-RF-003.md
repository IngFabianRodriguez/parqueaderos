# SPEC-01-003 — Historial de ocupación por hora

## Metadata
- **RF origen**: RF-003
- **Módulo**: 01-disponibilidad
- **Prioridad**: Media
- **Servicios**: parking-service, reporting-service

---

## User Story
**Como** Administrador de sede, gerente de operaciones **quiero** consultar el historial de ocupación hora por hora para un día específico **para** analizar patrones de demanda para tomar decisiones de staffing y tarifación.

## Objetivo
Proveer un reporte horneado del nivel de ocupación de la sede, mostrando para cada hora: espacios ocupados, tasa de ocupación, ingresos generados y duración promedio de parqueo. Permite al administrador hacer análisis de tendencias diarias y semanales.

## Comportamiento Específico

### Happy Path
1. Administrador abre el dashboard de reportes y selecciona 'Historial de ocupación'
2. Sistema muestra formulario con selector de sede y rango de fechas
3. Administrador selecciona fecha o rango de fechas
4. Sistema recibe GET /api/v1/sedes/{sede_id}/ocupacion/historial?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
5. Sistema consulta tabla registro_parqueo agregando por hora
6. Sistema retorna JSON con array de objetos por hora y métricas agregadas

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Rango > 31 días | Retorna 400 con mensaje 'Rango máximo 31 días' |
| Fecha sin transacciones | Retorna 200 con registro en 0 para todas las horas |
| Sede sin configuración de zonas | Agrega todos los espacios en una única zona 'General' |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| fecha_inicio | DATE | Fecha inicial del rango (formato YYYY-MM-DD) | Sí |
| fecha_fin | DATE | Fecha final del rango (formato YYYY-MM-DD) | Sí |
| zona_id | UUID | Filtrar por zona específica | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| fecha | DATE | — |
| hora | INTEGER | Hora del día (0-23) |
| ocupados_pico | INTEGER | — |
| tasa_ocupacion | DECIMAL(5,2) | — |
| transacciones | INTEGER | — |
| ingresos | DECIMAL(10,2) | — |
| duracion_promedio_min | INTEGER | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Retorna exactamente 24 registros para cada día consultado (uno por hora)
2. Los datos se generan en menos de 3 segundos para un rango de 7 días
3. Tasa de ocupación se calcula como promedio ponderado por tiempo

## Endpoints
- `GET /api/v1/sedes/{sede_id}/ocupacion/historial` — Historial horneado de ocupación

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- La tasa de ocupación por hora = (ocupados_pico / capacidad_total) * 100
- Si no hay transacciones en una hora específica, se retorna hora con ceros pero con el registro presente
- duracion_promedio_min se calcula solo sobre transacciones completadas (no espacios aún ocupados)
- ingresos agregados son sumatoria de valor_cobrado de las transacciones de esa hora