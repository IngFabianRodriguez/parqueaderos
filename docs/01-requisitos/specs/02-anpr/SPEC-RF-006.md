# SPEC-02-006 — Buscar placa a la salida, calcular duración y aplicar tarifa

## Metadata
- **RF origen**: RF-006
- **Módulo**: 02-anpr
- **Prioridad**: Alta
- **Servicios**: anpr-service, parking-service, billing-service

---

## User Story
**Como** Sistema ANPR (cámara de salida), Operador (fallback manual) **quiero** buscar la placa a la salida, calcular el tiempo de parqueo y aplicar la tarifa correspondiente **para** cobrarle al cliente el valor correcto basado en el tiempo exacto que usó el parqueadero.

## Objetivo
Cuando un vehículo llega a la salida, el sistema ANPR captura y reconoce la placa, busca el registro de entrada activo más reciente para esa placa, calcula la duración del parqueo, consulta la regla de tarifación vigente y determina el monto a cobrar. Si el cliente tiene saldo prepago, se descuenta del wallet. Si no, se genera la transacción de cobro.

## Comportamiento Específico

### Happy Path
1. Sensor de presencia detecta vehículo en la salida
2. ANPR-service captura imagen de placa y ejecuta OCR
3. ANPR-service envía placa a parking-service para buscar entrada activa
4. Parking-service consulta registro_entrada WHERE placa = X AND sede_id = Y AND salida IS NULL
5. Parking-service calcula duración = timestamp_salida - timestamp_entrada
6. Parking-service envía solicitud a billing-service con duración y sede_id
7. Billing-service consulta regla de tarifación vigente para la sede
8. Billing-service calcula tarifa: dependiendo de tarifas por minuto/hora/franja
9. Si cliente tiene wallet con saldo suficiente → se descuenta y se marca como pagado
10. Si no hay wallet o saldo insuficiente → se genera transacción pendiente de pago
11. Parking-service actualiza registro de entrada con timestamp_salida y valor_cobrado
12. Parking-service actualiza espacio a 'libre'
13. Parking-service emite evento 'salida_registrada' y 'cobro_generado'
14. Si pago confirmado → IoT-Gateway abre talanquera. Si no → se mantiene cerrada

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| No se encuentra entrada activa para la placa | Se bloquea salida, se registra en log y se alerta al operador |
| Entrada hace más de 24 horas (estancia máxima) | Se aplica tarifa máxima del día (cap) y se notifica al operador |
| Placa con múltiples entradas activas (error) | Se usa la entrada más antigua sin cerrar y se loguea anomalía |
| Cliente con descuento activo que cubre la estancia | Se marca como exonerado y se abre talanquera sin cobro |
| Saldo wallet insuficiente | Se genera transacción pendiente y talanquera permanece cerrada |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| placa | VARCHAR(20) | Texto de la placa capturada por OCR | Sí |
| imagen_placa | BINARY | Imagen de la placa para auditoría | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| salida_id | UUID | — |
| entrada_id | UUID | — |
| duracion_minutos | INTEGER | — |
| valor_cobrado | DECIMAL(10,2) | — |
| estado_pago | VARCHAR | pagado, pendiente, exonerado |
| metodo_pago | VARCHAR | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Cálculo de tarifa con precisión de minutos (redondeo hacia arriba)
2. Tiempo de procesamiento desde detección hasta decisión de apertura: < 3 segundos
3. El espacio se libera inmediatamente después de confirmar el pago
4. Transacción de cobro es inmutable una vez creada

## Endpoints
- `POST /api/v1/salidas` — Registra salida y genera cobro

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- duracion_minutos = ceil((timestamp_salida - timestamp_entrada).total_seconds() / 60)
- La búsqueda de entrada activa usa índice sobre (placa, sede_id) para optimizar
- Si el vehículo tiene reserva activa, se aplica la tarifa de reserva (no la umum)
- valor_cobrado puede ser 0 si hay descuentoactivo o promoción vigente
- El espacio solo se libera si estado_pago = 'pagado' o 'exonerado'; si es 'pendiente' el espacio permanece ocupado