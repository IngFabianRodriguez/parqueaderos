# SPEC-09-observabilidad-100 — Cada microservicio del sistema debe exponer un endpoint HTTP `GET /health` qu...

## Metadata
- **RF origen**: RF-100
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** que cada microservicio expose un endpoint `/health` que retorne el estado de sus dependencias **para** poder detectar rápidamente cuándo un servicio está fallando o degradado. ---

## Objetivo
Cada microservicio del sistema debe exponer un endpoint HTTP `GET /health` que permita verificar su estado operativo. El endpoint debe incluir el estado de la base de datos, dependencias externas (Redis, brokers de mensaje, APIs de terceros) y uso de memoria. Este endpoint será consumido por balanceadores de carga, orquestadores y el dashboard de salud general. ---

## Comportamiento Específico

### Happy Path
1. Un cliente (balanceador, orquestador, dashboard) envía `GET /health` al microservicio. 2. El microservicio ejecuta un health check paralelo sobre: - **DB principal**: Query `SELECT 1` o equivalente. - **Redis** (si aplica): Ping al servidor Redis. - **Brokers de mensaje** (si aplica): Conexión activa al broker. - **APIs externas críticas**: Request HEAD a la URL configurada con timeout de 3s. - **Memoria**: Lectura de `os.Getpid()` RSS o similar. 3. El microservicio compila los resultados en un JSON estructurado. 4. El servicio retorna el JSON con el código HTTP correspondiente. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
|| Campo | Tipo | Descripción | |---|-------|------|-------------| | service | string | Nombre del servicio (ej: "billing-service") | | version | string | Versión semver del servicio | | timestamp | datetime | Momento del health check (ISO 8601) | | status | enum | `UP`, `DEGRADED`, `DOWN` | | dependencies | array | Lista de dependencias con nombre, estado, latencia | | memory | object | Métricas de memoria del proceso | ---

## Datos de Salida
|| Campo | Tipo | Descripción | |---|-------|------|-------------| | service | string | Nombre del servicio (ej: "billing-service") | | version | string | Versión semver del servicio | | timestamp | datetime | Momento del health check (ISO 8601) | | status | enum | `UP`, `DEGRADED`, `DOWN` | | dependencies | array | Lista de dependencias con nombre, estado, latencia | | memory | object | Métricas de memoria del proceso | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Cada microservicio expone `GET /health` sin autenticación. 2. El endpoint responde en < 100 ms (sin contar timeouts de dependencias). 3. El estado de la DB se verifica con una query real, no solo conexión TCP. 4. Los estados `UP`/`DEGRADED`/`DOWN` se determinan según las reglas definidas. 5. El campo `memory.rss_mb` refleja el uso real de memoria del proceso. 6. Si el servicio tiene múltiples bases de datos (replica), se checkea la primaria. 7. El health check es idempotente (no modifica estado). 8. El dashboard puede hacer polling cada 30s sin impacto en rendimiento. ---

## Endpoints
- `GET /health` — Health check del microservicio (este es el endpoint que cada servicio expone). - `GET /health/live` — Liveness probe (solo verifica que el proceso está vivo). - `GET /health/ready` — Readiness probe (verifica que puede recibir tráfico). ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El endpoint `/health` no requiere autenticación para facilitar los probes de Kubernetes. - Se recomienda cachear el resultado del health check por 5-10s para evitar sobrecarga en la DB si hay muchos GET simultáneos, pero el cache debe invalidarse inmediatamente si una dependencia cambia de estado. - El campo `gc_triggered` en `memory` es un booleano que indica si el último health check detectó que se ejecutó un Garbage Collection recientemente (útil para detectar memory pressure).
