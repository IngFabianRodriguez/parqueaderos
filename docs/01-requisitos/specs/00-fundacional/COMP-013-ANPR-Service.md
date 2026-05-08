# COMP-013 — ANPR Service

## Metadata

- **Nombre**: anpr-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8004
- **DB**: PostgreSQL (schema `anpr`)
- **Servicios afectados**: iot-service, payments-service, sede-service

---

## Objetivo

Procesar imágenes de cámaras ANPR (Automatic Number Plate Recognition) para extraer placas vehiculares, enriquecer eventos de IoT con datos de reconocimiento, almacenar historial de lecturas, y detectar anomalías (vehículos duplicados, placas sospechosas).

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **OCR Engine**: LPRNet (modelo entrenado para placas colombianas) + OpenCV
- **Inference**: ONNX Runtime para GPU acceleration
- **DB**: PostgreSQL 15 (para almacenamiento de lecturas)
- **Cache**: Redis (cache de placas recientes, deduplicate)
- **Message Broker**: Kafka (topic `anpr.events`)
- **Storage**: S3 (imágenes raw y procesadas)

---

## Modelo de Datos

### Tabla: lecturas_placa

```
id                  UUID PK
tenant_id           UUID FK → tenants
sede_id             UUID FK → sedes
dispositivo_id      UUID FK → dispositivos (cámara ANPR)
ingreso_id          UUID FK → ingresos (nullable)
timestamp           TIMESTAMPTZ NOT NULL
plate_raw           VARCHAR(20) NOT NULL  -- texto extraído tal cual
plate_normalized    VARCHAR(20) NOT NULL  -- plate formateado standard
confidence          DECIMAL(5,4) NOT NULL  -- 0.0000 a 1.0000
country             VARCHAR(3) DEFAULT 'COL'
region              VARCHAR(10)  -- 'CUNDINAMARCA', 'ANTIOQUIA', etc
bbox_x1              INTEGER
bbox_y1              INTEGER
bbox_x2              INTEGER
bbox_y2              INTEGER
image_path          VARCHAR(500)  -- S3 path a imagen original
image_cropped_path  VARCHAR(500) -- S3 path a recorte placa
processing_time_ms  INTEGER
source               VARCHAR(30)  -- camera, manual, api
created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: vehiculos_conocidos

```
id              UUID PK
tenant_id       UUID FK → tenants
placa_normalized VARCHAR(20) NOT NULL UNIQUE
marca           VARCHAR(50)
modelo          VARCHAR(50)
color           VARCHAR(30)
tipo            VARCHAR(20)  -- particular, publico, moto, etc
cliente_id      UUID FK → clientes (nullable)
estado          VARCHAR(20) DEFAULT 'activo'
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: eventos_placa

```
id              UUID PK
lectura_id      UUID FK → lecturas_placa
tipo_evento     VARCHAR(50) NOT NULL  -- entrada, salida, pico_placa, vehiculo_bloqueado
timestamp       TIMESTAMPTZ NOT NULL
detecciones     JSONB DEFAULT '[]'  -- [{type, detail, confidence}]
created_at      TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints

### POST /api/v1/anpr/process
Procesar imagen para extraer placa.
```json
{
  "image_base64": "base64...",
  "sede_id": "uuid",
  "dispositivo_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z"
}
```
**Response 200**:
```json
{
  "plate_raw": "ABC123",
  "plate_normalized": "ABC123",
  "confidence": 0.9542,
  "country": "COL",
  "bbox": { "x1": 120, "y1": 340, "x2": 580, "y2": 400 },
  "processing_time_ms": 87,
  "image_cropped_url": "https://s3.../crops/uuid.jpg"
}
```

### POST /api/v1/anpr/process-url
Procesar imagen desde URL (cámara envía URL en vez de base64).
```json
{
  "image_url": "http://camera-ip/capture.jpg",
  "sede_id": "uuid",
  "dispositivo_id": "uuid"
}
```

### GET /api/v1/anpr/placas/:plate/history
Historial de lecturas de una placa.
**Query params**: `from`, `to`, `sede_id`, `limit`
```json
{
  "plate": "ABC123",
  "lecturas": [
    {
      "id": "uuid",
      "sede_id": "uuid",
      "sede_nombre": "Sede Centro",
      "timestamp": "2026-01-15T10:30:00Z",
      "tipo": "entrada",
      "confidence": 0.9542,
      "image_url": "https://s3.../uuid.jpg"
    }
  ]
}
```

### GET /api/v1/anpr/vehiculos
Lista vehículos conocidos.
**Query params**: `tenant_id`, `placa`, `cliente_id`, `limit`

### POST /api/v1/anpr/vehiculos
Registrar vehículo conocido manualmente.
```json
{
  "placa": "ABC123",
  "marca": "Toyota",
  "modelo": "Corolla",
  "color": "Blanco",
  "tipo": "particular"
}
```

### GET /api/v1/anpr/alertas
Alertas de anomalías detectadas.
**Query params**: `tenant_id`, `tipo`, `from`, `to`, `resolved`

### POST /api/v1/anpr/alertas/:id/resolve
Resolver alerta.

### POST /api/v1/anpr/validate
Validar placa contra lista de vehículos bloqueados (llamado por iot-service antes de abrir talanquera).
```json
{
  "plate": "ABC123",
  "sede_id": "uuid"
}
```
**Response 200**:
```json
{
  "valid": true,
  "plate": "ABC123",
  "cliente_id": "uuid",
  "riesgo": "low",
  "matched_vehicle_id": "uuid"
}
```
**Response 200 (bloqueado)**:
```json
{
  "valid": false,
  "plate": "ABC123",
  "riesgo": "high",
  "motivo": "vehículo_bloqueado",
  "alerta_id": "uuid"
}
```

### POST /api/v1/anpr/manual-entry
Registrar lectura manual (plate + timestamp), sin imagen.
```json
{
  "plate": "ABC123",
  "sede_id": "uuid",
  "dispositivo_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "tipo": "entrada",
  "operador_id": "uuid"
}
```

### GET /api/v1/anpr/stats/occupancy
Estadísticas de occupancy basadas en lecturas ANPR (para validación cruzada con sensors).
**Query params**: `sede_id`, `from`, `to`

---

## Flujo de Procesamiento

### Imagen Recibida (desde iot-service)

```
1. iot-service detecta vehículo en zona de captura
2. Publica evento en Kafka iot.events con imagen_url o base64
3. anpr-service consume evento
4. Descarga imagen desde URL (o decodifica base64)
5. Pre-procesamiento: resize, normalize, adjust contrast
6. Inference LPRNet → texto raw + confidence + bbox
7. Normalización: uppercase, remover espacios inválidos, format COL
8. Deduplicación: check Redis para placa reciente (< 5min same sede)
9. Guardar lectura en BD
10. Subir imagen recortada a S3
11. Publicar evento en anpr.events
12. Si es entrada: crear/update vehículo conocido
13. Evaluar alertas: vehículo bloqueado, pico-y-placa, etc
```

### Validación para Abrir Talanquera

```
1. iot-service → POST /anpr/validate (plate, sede_id)
2. anpr-service busca placa en vehiculos_conocidos
3. Verifica estado = 'activo'
4. Busca alertas pendientes para esa placa
5. Evalúa reglas pico-y-placa (dia actual)
6. Retorna valid + riesgo
7. iot-service decide si abre o no
```

---

## Algoritmo LPRNet

### Entrenamiento

- Dataset: 50k imágenes de placas colombianas
- Formatos: placa antigua (3 letras + 3 nums), nueva (4 nums + 3 letras)
- Augmentations: rotation ±5°, brightness, blur, rain

### Inference

```python
# ONNX Runtime
session = InferenceSession("lprnet.onnx")
input_tensor = preprocess_image(img, shape=(3, 94, 24))
output = session.run(None, {"input": input_tensor})
plate_text = decode_output(output[0])  # CTC decoder
confidence = calculate_confidence(output[0])
```

### Post-procesamiento

1. Uppercase normalization
2. Remove special chars (solo alfanumérico)
3. Validate against Colombian plate regex
4. If confidence < 0.7 → marcar como baja confianza, requerir validación manual
5. Si plate no match regex → discard como lectura inválida

---

## Deduplicación

### Redis Cache

```
Key: anpr:plate:{sede_id}:{normalized_plate}
Value: { lectura_id, timestamp }
TTL: 300s (5 minutos)
```

### Lógica

- Si llega lectura con misma placa + misma sede en < 5 min → duplicate
- Guardar siempre, marcar `is_duplicate: true` en eventos_placa
- No generar alerta si es duplicate de lectura anterior

---

## Pico y Placa

### Reglas Colombia

```python
# Pico y Placa Bogotá (ejemplo)
RESTRICTION_MAP = {
    'LUNES': ['1', '2'],
    'MARTES': ['3', '4'],
    'MIERCOLES': ['5', '6'],
    'JUEVES': ['7', '8'],
    'VIERNES': ['9', '0'],
}
```

### Validación

- Se consulta antes de abrir talanquera en hora pico (6-9am, 4-8pm)
- Si restricción aplica → generar alerta, no bloquea automáticamente
- Administrador puede override

---

## S3 Storage

### Estructura de directorios

```
anpr-images/
├── raw/
│   └── {tenant_id}/
│       └── {sede_id}/
│           └── {YYYY-MM-DD}/
│               └── {dispositivo_id}/
│                   └── {timestamp}_{plate}.jpg
├── cropped/
│   └── {lectura_id}/
│       └── plate.jpg
└── alerts/
    └── {alerta_id}/
        └── evidence.jpg
```

### Políticas

- Raw images: retention 30 días, luego delete
- Cropped plates: retention 1 año
- Bilder alert: retention 2 años

---

## Kafka Events

### Topic: anpr.events

```json
{
  "event_id": "uuid",
  "tenant_id": "uuid",
  "sede_id": "uuid",
  "lectura_id": "uuid",
  "plate_normalized": "ABC123",
  "event_type": "entrada_detected",
  "confidence": 0.9542,
  "timestamp": "2026-01-15T10:30:00Z"
}
```

```json
{
  "event_id": "uuid",
  "event_type": "alerta_generada",
  "alerta_id": "uuid",
  "plate": "ABC123",
  "tipo": "pico_placa",
  "riesgo": "medium",
  "timestamp": "2026-01-15T07:30:00Z"
}
```

---

## Dependencias

- **DB**: PostgreSQL `anpr` schema
- **Redis**: deduplicación y cache
- **Kafka**: anpr.events
- **S3**: almacenamiento de imágenes
- **iot-service**: fuente de eventos de cámaras
- **ml-model**: LPRNet ONNX model (stored in S3)
- **notif-service**: alertas a operadores

---

## Métricas

- `anpr_readings_total{sede_id, confidence_bucket}`
- `anpr_processing_duration_ms`
- `anpr_confidence_avg`
- `anpr_alerts_total{tipo}`
- `anpr_duplicates_total`
- `anpr_validations_total{result}`
- `anpr_vehiculos_known_total`

---

## Health Checks

`GET /health` → `{ "status": "ok", "model_loaded": true, "onnx_runtime": "ok" }`
`GET /health/ready` → DB + Redis + modelo ONNX cargado
`GET /health/live` → proceso corriendo

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Imagen corrupta | 400 Bad Request, log para debug |
| Modelo no carga | Fallback a modo manual, alertas ops |
| Confidence < 0.7 | Guardar lectura, generar alerta validación manual |
| Placa no reconocida | Generar alerta "plate_unrecognized", iot-service decide |
| S3 down | Buffer imágenes en disco local (max 1GB), retry |
| Lectura duplicate | Deduplicar, no generar nuevos eventos |
| Vehículo bloqueado | Generar alerta y bloquear apertura |
| Hora pico + placa restringida | Generar alerta, no bloquear automáticamente |