# SPEC-09-observabilidad-106 — El `tenant_admin` debe poder configurar, desde la interfaz de administración,...

## Metadata
- **RF origen**: RF-106
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** `tenant_admin` **quiero** configurar los umbrales (thresholds) de alerta para cada métrica **para** recibir notificaciones cuando el sistema se comporta fuera de los parámetros normales sin necesidad de contactar al equipo de desarrollo. ---

## Objetivo
El `tenant_admin` debe poder configurar, desde la interfaz de administración, umbrales de alerta personalizados para cualquier métrica disponible (CPU, RAM, latencia, error rate, etc.). Cada umbral define: la métrica objetivo, el valor threshold, el operador de comparación (> , < , >=), la severidad de la alerta (CRITICAL, WARNING, INFO), y el mensaje de notificación. Los umbrales se almacenan por tenant y se aplican a todos los servicios o a servicios específicos. ---

## Comportamiento Específico

### Happy Path
1. El `tenant_admin` accede a `Observabilidad → Alertas → Configurar Thresholds`. 2. El sistema muestra una lista de métricas disponibles organizadas por categoría. 3. El admin puede crear un nuevo umbral: - Selecciona la métrica (ej: `process_cpu_percent`). - Selecciona el servicio (o "todos los servicios"). - Define el operador (`>`, `>=`, `<`, `<=`) y el valor threshold. - Selecciona la severidad: `CRITICAL`, `WARNING`, `INFO`. - Define el mensaje de notificación (template con variables). - Define la ventana de evaluación: cada cuánto se evalúa (default: 1min). - Define la condición: "se activa si se viola N veces consecutivas" (default: 1). 4. El umbral se guarda en `alert_thresholds` y se activa inmediatamente. 5. El sistema evalúa continuamente las métricas contra los umbrales activos. 6. Cuando se cruza el umbral, se genera una alerta que se envía por los canales configurados. ---

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
1. El `tenant_admin` puede crear, editar, eliminar y desactivar thresholds desde la UI. 2. Cada threshold tiene: métrica, operador, valor, severidad, mensaje, servicio, intervalo de evaluación. 3. Los thresholds se evalúan contra los valores de métricas en tiempo real. 4. Una alerta se genera cuando la condición se cumple `consecutive_violations` veces seguidas. 5. Los mensajes de alerta usan templates con variables disponibles. 6. Los thresholds son específicos del tenant (aislamiento entre tenants). 7. Los thresholds activos se pueden listar y buscar. 8. Se puede clonar un threshold existente para crear uno similar. 9. Los thresholds son consistentes con la configuración de canales (RF-107) y ventanas de silencio (RF-108). ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/alert-thresholds` — Listar thresholds - `POST /api/v1/tenants/{tenant_id}/alert-thresholds` — Crear threshold - `PUT /api/v1/tenants/{tenant_id}/alert-thresholds/{threshold_id}` — Actualizar threshold - `DELETE /api/v1/tenants/{tenant_id}/alert-thresholds/{threshold_id}` — Eliminar threshold - `PATCH /api/v1/tenants/{tenant_id}/alert-thresholds/{threshold_id}/activate` — Activar - `PATCH /api/v1/tenants/{tenant_id}/alert-thresholds/{threshold_id}/deactivate` — Desactivar ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda que los thresholds de producción tengan `consecutive_violations >= 2` para evitar falsos positivos por spikes. - Para métricas de latencia, el threshold debe definirse en la misma unidad que la métrica (segundos para durations). - La evaluación de thresholds puede delegarse a Prometheus AlertManager (externo) o implementarse internamente con un worker que haga polling a Prometheus. - Si el tenant tiene muchos thresholds (> 100), se debe implementar paginación en el listado. - Los thresholds deben poder importarse/exportarse en JSON para backup y migración.
