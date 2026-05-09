# SPEC-11-app-operador-140 — El operador tiene una función de búsqueda integrada en la app que le permite ...

## Metadata
- **RF origen**: RF-140
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** buscar un cliente por nombre, placa o teléfono y ver su historial completo **para** atender rápidamente consultas, resolver problemas y tener contexto del cliente. ---

## Objetivo
El operador tiene una función de búsqueda integrada en la app que le permite encontrar clientes (propietarios de vehículos) usando cualquiera de tres criterios: nombre, placa o número de teléfono. Una vez encontrado, el sistema muestra el perfil del cliente con su historial completo de movimientos, pagos, bloqueos y observaciones. ---

## Comportamiento Específico

### Happy Path
1. El operador toca la barra de búsqueda en la app (dashboard o menú). 2. El operador ingresa al menos 3 caracteres en cualquiera de los campos: - Nombre (búsqueda parcial, sin distinción de mayúsculas/minúsculas). - Placa (búsqueda exacta o parcial). - Teléfono (búsqueda exacta). 3. El sistema muestra resultados en tiempo real a medida que se escribe (mínimo 3 caracteres). 4. El operador selecciona un cliente de la lista. 5. Se muestra el perfil del cliente con: - Datos personales: nombre, teléfono, email. - Vehículos asociados: lista de placas. - Estado de cuenta: tiene saldo pendiente, tiene bloqueo activo. - Historial de movimientos: últimos 50 registros. 6. El operador puede navegar a acciones desde el perfil: ver ticket abierto, desbloquear vehículo, etc. ---

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
1. La búsqueda devuelve resultados en < 1 segundo para textos de 3+ caracteres. 2. La búsqueda por placa es la más rápida y precisa. 3. El operador puede buscar sin saber exactamente qué criterio usar. 4. El perfil del cliente muestra de un vistazo si tiene bloqueos o deudas pendientes. 5. El historial muestra los últimos 50 movimientos sin paginación visible. 6. Se puede acceder a cualquier ticket abierto desde el perfil del cliente. 7. Los datos del cliente se actualizan en tiempo real si hay cambios. 8. La búsqueda funciona offline si se tienen datos en caché de clientes frecuentes. ---

## Endpoints
- `GET /api/v1/operator/customers/search?q={query}&type={nombre|placa|telefono}` — Búsqueda - `GET /api/v1/operator/customers/{id}` — Perfil completo - `GET /api/v1/operator/customers/{id}/vehicles` — Vehículos del cliente - `GET /api/v1/operator/customers/{id}/history?limit=50` — Historial ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La barra de búsqueda debe estar visible en el dashboard para acceso rápido. - Se debe recordar las últimas 10 búsquedas del operador para acceso offline. - El historial debe ser exportable a CSV si el supervisor lo solicita. - Si el cliente tiene múltiples vehículos, se debe poder ver el estado de cada uno por separado.
