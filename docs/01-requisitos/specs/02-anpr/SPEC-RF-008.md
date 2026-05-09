# SPEC-02-008 — Operar en modo offline y sincronizar al reconectar

## Metadata
- **RF origen**: RF-008
- **Módulo**: 02-anpr
- **Prioridad**: Alta
- **Servicios**: anpr-service, parking-service, iot-gateway

---

## User Story
**Como** Sistema (operación autónoma) **quiero** continuar operando cuando se pierde la conexión al servidor central, registrando entradas y salidas localmente **para** garantizar que el parqueadero sigue funcionando sin interrupciones aunque la conectividad a internet falle.

## Objetivo
Cuando el enlace de red al servidor central falla, los componentes IoT (ANPR, talanquera, sensores) deben continuar operando en modo autonomía local. Cada dispositivo mantiene una base de datos local con los últimos datos necesarios (tarifas vigentes, espacios disponibles, blacklist). Cuando la conexión se restablece, el sistema sincroniza todos los registros pendientes de manera ordenada, resolviendo conflictos.

## Comportamiento Específico

### Happy Path
1. IoT-Gateway detecta pérdida de conexión al servidor central (heartbeat timeout)
2. IoT-Gateway activa modo offline y notifica a ANPR-service y parking-service
3. ANPR-service comienza a almacenar registros localmente (SQLite local)
4. Vehículos siguen entrando y saliendo: ANPR captura placa, busca en cache local, registra entrada/salida
5. Tarifas se calculan con datos locales (última sincronización)
6. Cuando la conexión se restablece, parking-service envía cola de sincronización
7. Servidor central recibe cada registro, detecta timestamp, y determina si es entrada o salida
8. Servidor procesa en orden cronológico, resolviendo conflictos de estados
9. Sistema genera reporte de sincronización

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Entrada offline, salida online (vehículo salió mientras sistema estaba caído) | Se detecta por timestamp: la salida online se procesa primero y la entrada offline se marca como 'sincronizada_con_conflicto' |
| Registro duplicado (misma placa dos entradas offline) | Se toma la más reciente y se loguea la anomalía |
| Tarifa cambió mientras estuvo offline | Se usa la tarifa vigente al momento del registro, no la actual |
| Datos locales corruptos | Se requiere intervención manual y se genera alerta |
| Sincronización > 48 horas | El sistema entra en modo de solo lectura y no permite nuevas transacciones hasta sincronizar |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| cola_registros | ARRAY | Array de registros realizados offline | Sí |
| device_id | UUID | Identificador del dispositivo IoT | Sí |
| ultima_sincronizacion | TIMESTAMP | Timestamp de última sincronización exitosa | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| sincronizados | INTEGER | — |
| conflictos | ARRAY | — |
| timestamp_sincronizacion | TIMESTAMP | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. El sistema puede operar hasta 48 horas en modo offline sin perder datos críticos
2. La sincronización no genera duplicación de transacciones
3. Todos los registros offline tienen un identificador único generado localmente que se preserva en la sincronización

## Endpoints
- `POST /api/v1/sync/cola` — Sincroniza cola de registros offline

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Cada registro offline tiene un uuid_local generado por SQLite que se preserva en la sincronización
- El servidor central usa el uuid_local para deduplicar: si ya existe un registro con el mismo uuid_local, se ignora
- Los conflictos se loguean con tipo: DUPLICATE_ENTRY, TIMESTAMP_MISMATCH, STATE_CONFLICT
- La cola de registros se envía en lotes de hasta 100 registros por solicitud
- El servidor responde con el conteo de sincronizados y la lista de conflictos detectados
- Para tarifas offline se usa la última versión sincronizada: el campo version en la tabla tarifa_local