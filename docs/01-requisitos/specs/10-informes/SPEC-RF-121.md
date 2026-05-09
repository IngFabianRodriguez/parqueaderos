# SPEC-10-informes-121 — El sistema debe generar, a partir de los datos históricos de ocupación (RF-11...

## Metadata
- **RF origen**: RF-121
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sede_admin o tenant_admin **quiero** ver una proyección de ocupación futura basada en patrones históricos **para** planificar capacidad, horarios del personal y campañas de precio dinámico. ---

## Objetivo
El sistema debe generar, a partir de los datos históricos de ocupación (RF-119), una predicción de la ocupación esperada para los próximos días/semanas. Se usará un modelo de forecasting que considere patrones por día de la semana y hora (estacionalidad semanal) y tendencias de largo plazo. ---

## Comportamiento Específico

### Happy Path
1. El usuario solicita el forecast specifying: sede, fecha_inicio_proyeccion, fecha_fin_proyeccion, y opcionalmente horizonte en días 2. El `forecasting-service` consulta los datos históricos de ocupación (RF-119) — mínimo 4 semanas previas 3. El modelo detecta patrones: a. Estacionalidad semanal: diferente ocupación por día de la semana b. Estacionalidad horaria: diferente ocupación por hora del día c. Tendencia: crecimiento o Decline de la ocupación en el tiempo 4. Se genera la predicción para cada hora de cada día en el horizonte seleccionado 5. Se calcula el intervalo de confianza (por defecto ± 2 desviaciones estándar) 6. Se retorna la serie temporal proyectada con bandas de confianza ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | modelo_utilizado | string | Nombre del modelo de forecasting usado | | fecha_historico_desde | date | Inicio de los datos históricos usados | | fecha_historico_hasta | date | Fin de los datos históricos usados | | proyeccion | array | Array de objetos con fecha, hora, ocupacion_predicha, intervalo_superior, intervalo_inferior | | proyeccion[].fecha | date | Fecha de la predicción | | proyeccion[].hora | integer | Hora del día (0-23) | | proyeccion[].ocupacion_predicha | decimal | Tasa de ocupación predicha (%) | | proyeccion[].intervalo_superior | decimal | Límite superior del intervalo de confianza (%) | | proyeccion[].intervalo_inferior | decimal | Límite inferior del intervalo de confianza (%) | | resumen | object | Máxima ocupación predicha, mínima, promedio en el horizonte | | alertas | array | Lista de horarios/días donde la ocupación predicha supera el 90% | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | uuid | Identificador de la sede | | modelo_utilizado | string | Nombre del modelo de forecasting usado | | fecha_historico_desde | date | Inicio de los datos históricos usados | | fecha_historico_hasta | date | Fin de los datos históricos usados | | proyeccion | array | Array de objetos con fecha, hora, ocupacion_predicha, intervalo_superior, intervalo_inferior | | proyeccion[].fecha | date | Fecha de la predicción | | proyeccion[].hora | integer | Hora del día (0-23) | | proyeccion[].ocupacion_predicha | decimal | Tasa de ocupación predicha (%) | | proyeccion[].intervalo_superior | decimal | Límite superior del intervalo de confianza (%) | | proyeccion[].intervalo_inferior | decimal | Límite inferior del intervalo de confianza (%) | | resumen | object | Máxima ocupación predicha, mínima, promedio en el horizonte | | alertas | array | Lista de horarios/días donde la ocupación predicha supera el 90% | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La proyección cubre cada hora de cada día en el horizonte solicitado 2. El intervalo de confianza incluye el valor real con la probabilidad del `nivel_confianza` configurado 3. Si la ocupación predicha supera el 90%, se genera una alerta en el campo `alertas` 4. El forecast se actualiza automáticamente si se regenera con nuevos datos históricos 5. El tiempo de generación del forecast es < 30 segundos ---

## Endpoints
- `GET /api/v1/reports/occupancy/forecast` — Genera la proyección - `GET /api/v1/reports/occupancy/hourly` — Fuente de datos históricos ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El modelo de forecasting puede ser simple (promedio móvil con estacionalidad) o avanzado (SARIMA, Prophet) según la complejidad del histórico - Se recomienda guardar el error histórico del forecast para calibrar el modelo - Las alertas de ocupación > 90% ayudan al sede_admin a planificar personal adicional - La proyección es solo informativa; no genera automáticamente acciones de pricing
