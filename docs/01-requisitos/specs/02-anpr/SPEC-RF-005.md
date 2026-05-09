# SPEC-02-005 — Capturar placa a la entrada y registrar timestamp

## Metadata
- **RF origen**: RF-005
- **Módulo**: 02-anpr
- **Prioridad**: Alta
- **Servicios**: anpr-service, parking-service, iot-gateway

---

## User Story
**Como** Sistema ANPR (cámara de entrada), Operador (fallback manual) **quiero** capturar automáticamente la placa del vehículo al cruzar la entrada y registrar la hora exacta **para** tener un registro confiable de la hora de entrada para calcular la tarifa correctamente.

## Objetivo
Cuando un vehículo cruza el sensor de entrada, el sistema ANPR captura la imagen de la placa, ejecuta OCR para extraer el texto de la placa, y registra un evento de entrada en el sistema con: placa, timestamp, sede, zona y número de espacio asignado. El sistema debe procesar la captura en menos de 2 segundos.

## Comportamiento Específico

### Happy Path
1. Sensor de presencia detecta vehículo en la entrada
2. IoT-Gateway envía evento 'vehiculo_detectado' a ANPR-service
3. ANPR-service activa cámara, captura imagen de la placa
4. ANPR-service ejecuta OCR sobre la imagen y extrae texto de placa
5. ANPR-service consulta espacio libre y asigna uno si disponible
6. ANPR-service envía comando a parking-service para registrar entrada
7. Parking-service crea registro en tabla registro_entrada con placa, timestamp, espacio_id, sede_id
8. Parking-service actualiza estado del espacio a 'ocupado'
9. Parking-service emite evento 'entrada_registrada' por websocket
10. IoT-Gateway envía comando de apertura de talanquera

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| OCR confianza < 70% | Se marca placa como 'PENDIENTE' y se dispara flujo de registro manual |
| Vehículo sin placa visible | Se registra como 'SIN-PLACA' y se emite alerta al operador |
| Placa ya tiene entrada abierta (vehículo aún dentro) | Se emite alerta de 'vehículo duplicado' y se loguea sin abrir talanquera |
| Sensor de cámara falla | Se activa modo de fallback: entrada manual por operador |
| No hay espacios disponibles | Se muestra alerta al operador y se bloquea la entrada |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sede_id | UUID | Identificador de la sede | Sí |
| zona_id | UUID | Identificador de zona de entrada | Sí |
| imagen_placa | BINARY | Imagen capturada por la cámara (base64) | Sí |
| sensor_id | UUID | Identificador del sensor que detectó el vehículo | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| entrada_id | UUID | — |
| placa | VARCHAR(20) | Texto de la placa extraído por OCR |
| timestamp_entrada | TIMESTAMP | — |
| espacio_id | UUID | — |
| confianza_ocr | DECIMAL(5,2) | Porcentaje de confianza del OCR (0-100) |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Tiempo total desde detección del sensor hasta registro en base de datos: < 2 segundos
2. OCR extrae placa con exactitud del 95% en condiciones normales de iluminación
3. Se asigna espacio libre antes de abrir la talanquera
4. El registro de entrada es inmutable una vez creado (no se elimina ni modifica)

## Endpoints
- `POST /api/v1/entradas` — Registra una nueva entrada de vehículo
- `WS /ws/entradas` — Notifica nuevas entradas en tiempo real

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Placa se normaliza a mayúsculas sin espacios antes de guardar (ej: "ABC-123" → "ABC123")
- Si confianza_ocr < 70%, el campo placa se marca como 'PENDIENTE' y se genera una tarea para registro manual
- El espacio se asigna usando estrategia first-fit: el primer espacio libre encontrado en la zona
- Si la sede tiene múltiples zonas de entrada, se usa zona_id del sensor que detectó el vehículo
- En modo manual (fallback), el endpoint es POST /api/v1/entradas/manual (ver RF-007)