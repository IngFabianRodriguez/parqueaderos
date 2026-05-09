# SPEC-09-observabilidad-101 — Un dashboard centralizado debe mostrar el estado de salud (`UP`, `DEGRADED`, ...

## Metadata
- **RF origen**: RF-101
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** ver un dashboard que muestre en tiempo real el estado de salud de todos los microservicios **para** detectar rápidamente cuál servicio está caído o degradado sin necesidad de consultar cada uno manualmente. ---

## Objetivo
Un dashboard centralizado debe mostrar el estado de salud (`UP`, `DEGRADED`, `DOWN`) de todos los microservicios del sistema. La información se actualiza automáticamente cada 30 segundos mediante polling a los endpoints `/health` de cada microservicio. El dashboard debe ser accesible desde la interfaz de administración y debe permitir filtrar por tenant, sede o tipo de servicio. ---

## Comportamiento Específico

### Happy Path
1. El `tenant_admin` accede a `Observabilidad → Dashboard de Salud`. 2. El sistema consulta el endpoint `/health` de todos los microservicios registrados. 3. El sistema compila los resultados y los muestra en una grilla/tarjeta por servicio. 4. Cada 30 segundos, el sistema vuelve a consultar todos los endpoints. 5. Si un servicio cambia de estado, se emite una notificación visual (toast/badge). 6. El operador puede hacer clic en un servicio para ver el detalle: dependencias, latencia, memoria. ---

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
1. El dashboard se actualiza cada 30 segundos automáticamente. 2. Todos los servicios registrados aparecen con su estado correcto. 3. Un servicio `DOWN` se muestra con fondo rojo y badge de alerta. 4. El operador puede filtrar por sede, tenant o tipo de servicio. 5. Al hacer clic en un servicio se muestran los detalles de sus dependencias. 6. Se muestra el `uptime_percent_30d` de cada servicio. 7. El operador puede exportar el estado actual a PDF o CSV. 8. El dashboard es accesible desde el menú principal de `Observabilidad`. 9. Si el operador no ha interactuado por 5 minutos, se sigue actualizando en background. ---

## Endpoints
- `GET /api/v1/observability/dashboard` — Dashboard principal - `GET /api/v1/observability/services` — Lista de servicios - `GET /api/v1/observability/services/{service_id}/detail` — Detalle de un servicio - `GET /api/v1/observability/services/{service_id}/history` — Historial de estados (para gráficos) - `WS /api/v1/observability/dashboard/live` — WebSocket para actualizaciones en tiempo real (opcional, mejora UX) ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El polling interval de 30s es configurable por el `tenant_admin` (mínimo 10s, máximo 5min). - Para mejorar rendimiento, se recomienda usar HTTP HEAD para los health checks. - Se debe implementar exponential backoff si un servicio está tardando más de 5s en responder. - El campo `down_since` permite saber hace cuánto tiempo está caído un servicio. - La vista de historial debe permitir ver hasta 30 días de estados para calcular uptime.
