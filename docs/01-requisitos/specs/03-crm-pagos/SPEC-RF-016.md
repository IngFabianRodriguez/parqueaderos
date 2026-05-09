# SPEC-03-016 — Gestionar cartera de morosos con bloqueo y desbloqueo de placas

## Metadata
- **RF origen**: RF-016
- **Módulo**: 03-crm-pagos
- **Prioridad**: Alta
- **Servicios**: crm-service, billing-service

---

## User Story
Como Admin del tenant **quiero** identificar, gestionar y recuperar las deudas de clientes morosos **para** proteger la operación del parqueadero y garantizar que los vehículos con deuda pendiente no puedan salir sin antes regularizar su situación.

## Objetivo
El sistema debe mantener una cartera de clientes morosos con deuda pendiente, permitir el bloqueo de sus placas para impedir la salida hasta que paguen, y gestionar el proceso de desbloqueo una vez la deuda esté cancelada.

## Comportamiento Específico
### Happy Path (Activación de bloqueo)
1. Cliente tiene sesiones pendientes de pago que exceden el umbral configurado
2. Sistema crea/actualiza registro en tabla `morosos`
3. Sistema cambia estado del vehículo a `bloqueado`
4. Sistema registra en auditoría
5. Si el vehículo intenta salir (ANPR detecta placa), la talanquera NO abre (ver RF-018)
6. Sistema envía notificación al cliente (RF-014): "Tiene deuda pendiente"

### Happy Path (Pago de deuda - desbloqueo)
1. Cliente paga la deuda (efectivo, transferencia, etc.)
2. Operador registra el pago
3. Sistema actualiza sesiones pendientes → pagadas
4. Sistema cambia estado del vehículo a `activo`
5. Notificación enviada al cliente: "Su vehículo ha sido desbloqueado"
6. Talanquera puede abrir normalmente

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Cliente con múltiples vehículos tiene deuda en solo uno | Solo se bloquea la placa con deuda. Las otras permanecen activas |
| Vehículo bloqueado intenta salir por ANPR | Talanquera no abre. Mensaje: "Placa bloqueada. Contacte administración" |
| Deuda pagada parcialmente | Se mantiene bloqueado hasta que esté pagada completamente |
| Acuerdo de pago realizado | Estado → `acuerdo_pago`. Se permite salida. Si incumple, vuelve a bloquear |
| Cliente con deuda se registra con nueva placa | La nueva placa también queda bloqueada hasta saldar deuda total |
| Error de sistema que bloquea sin deuda real | Admin puede desbloquear manualmente con motivo obligatorio |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| cliente_id | UUID | Cliente moroso | Sí |
| monto_total | DECIMAL | Suma de deudas pendientes | Auto |
| sesiones_pendientes | ARRAY[UUID] | IDs de sesiones con deuda | Auto |
| dias_mora | INTEGER | Días desde la primera deuda | Auto |
| estado_bloqueo | VARCHAR | bloqueado, observado, acuerdo_pago, desbloqueado | Sí |
| observaciones | TEXT | Notas del operador/admin | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| moroso_id | UUID | — |
| cliente_id | UUID | — |
| placas | ARRAY[VARCHAR] | Placas bloqueadas |
| monto_deuda | DECIMAL | Total pendiente |
| estado | VARCHAR | — |
| fecha_bloqueo | TIMESTAMP | — |
| intentos_contacto | INTEGER | — |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo vehículo bloqueado tiene al menos una sesión con deuda pendiente > X días (configurable)
2. Placa bloqueada no puede salir del parqueadero (talanquera no abre)
3. Desbloqueo automático al confirmar pago completo de la deuda
4. Cada intento de contacto con el moroso queda registrado
5. Políticas de bloqueo configurables por tenant: días de mora, monto mínimo para bloquear

## Endpoints
- `GET /api/v1/morosos` — Lista de morosos del tenant
- `GET /api/v1/morosos/{moroso_id}` — Detalle del moroso
- `POST /api/v1/morosos/{moroso_id}/contacto` — Registrar intento de contacto
- `POST /api/v1/morosos/{moroso_id}/desbloquear` — Desbloquear vehículo (pago o manual)
- `PUT /api/v1/morosos/politicas` — Configurar reglas de bloqueo del tenant

## Health Check
- `GET /health` → `{ "status": "ok", "service": "crm-service" }`

## Notas
- Bloqueo es soft block en el sistema — impide salida por la talanquera pero no involucra policía o acción legal.
- Tiempo para bloquear: configurable (ej: 72 horas después del vencimiento del pago).
- Monto mínimo para bloquear: configurable, típicamente 1 día de parqueo para evitar bloqueos por montos triviales.
- Customer contact history: se registra para prueba en caso de disputas.