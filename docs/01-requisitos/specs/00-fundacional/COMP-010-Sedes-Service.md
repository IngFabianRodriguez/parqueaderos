# COMP-010 — Sedes Service

## Metadata

- **Nombre**: sedes-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8003
- **DB**: PostgreSQL (schema `sedes`)
- **Cache**: Redis
- **Servicios afectados**: Todos los que operan por sede
- **Componentes relacionados**: tenant-service, iot-service, parking-service

---

## Objetivo

Gestionar las sedes (parqueaderos físicos) de cada tenant: CRUD de sedes, zonas, espacios, dispositivos IoT (talanqueras, cámaras ANPR), y configuración operativa por sede.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 15
- **Cache**: Redis (estados de espacios, configuración)
- **Message Broker**: Kafka (eventos IoT)
- **API**: REST + gRPC (interno)

---

## Modelo de Datos

### Tabla: sedes

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

nombre              VARCHAR(255) NOT NULL
codigo              VARCHAR(50) NOT NULL  -- código interno único por tenant
descripcion         TEXT
direccion           TEXT NOT NULL
ciudad              VARCHAR(100)
latitud             DECIMAL(10,8)
longitud            DECIMAL(11,8)

timezone            VARCHAR(50) DEFAULT 'America/Bogota'
currency            VARCHAR(3) DEFAULT 'COP'

estado              VARCHAR(20) DEFAULT 'active'  -- active, inactive, maintenance

horario_operacion   JSONB DEFAULT '{}'  -- { "lunes": { "open": "06:00", "close": "22:00" }, ... }

contacto_nombre     VARCHAR(255)
contacto_telefono   VARCHAR(50)
contacto_email      VARCHAR(255)

configuracion       JSONB DEFAULT '{}'  -- settings específicos de sede

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: zonas

```sql
id                  UUID PK
sede_id             UUID FK → sedes NOT NULL

nombre              VARCHAR(255) NOT NULL
codigo              VARCHAR(50) NOT NULL
descripcion         TEXT

tipo                VARCHAR(20)  -- general, discapacidad, electrico, Moto, carga
nivel               VARCHAR(50)  -- P1, P2, S1, S2, etc
orden               INTEGER DEFAULT 0

configuracion       JSONB DEFAULT '{}'

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: espacios

```sql
id                  UUID PK
sede_id             UUID FK → sedes NOT NULL
zona_id             UUID FK → zonas NOT NULL

numero              VARCHAR(20) NOT NULL  -- "A-001", "P1-05"
tipo_vehiculo       VARCHAR(20)  -- auto, Moto, carga, discapacidad

estado              VARCHAR(20) DEFAULT 'libre'  -- libre, ocupado, mantenimiento, reservado
estado_since        TIMESTAMPTZ  -- cuando cambió el estado

tags                VARCHAR(255)[] DEFAULT '{}'

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()

UNIQUE(sede_id, numero)
```

### Tabla: dispositivos

```sql
id                  UUID PK
sede_id             UUID FK → sedes NOT NULL

tipo                VARCHAR(30) NOT NULL  -- talanquera_entrada, talanquera_salida, camara_anpr, sensor_ocupacion

nombre              VARCHAR(255) NOT NULL
codigo              VARCHAR(50) NOT NULL
modelo              VARCHAR(100)

estado              VARCHAR(20) DEFAULT 'online'  -- online, offline, error, maintenance
last_seen           TIMESTAMPTZ
latencia_ms         INTEGER

configuracion       JSONB DEFAULT '{}'  -- IP, credentials, thresholds

zona_id             UUID FK → zonas (nullable)  -- específico para cameras

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: sede_events

```sql
id                  UUID PK
sede_id             UUID FK → sedes NOT NULL
event_type          VARCHAR(50) NOT NULL
metadata            JSONB DEFAULT '{}'
created_at          TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints REST

### Sedes

```
GET    /api/v1/sedes                    Lista sedes (filtro por tenant_id)
POST   /api/v1/sedes                    Crea sede
GET    /api/v1/sedes/{sede_id}          Detalle sede
PATCH  /api/v1/sedes/{sede_id}          Actualiza sede
DELETE /api/v1/sedes/{sede_id}          Elimina sede

GET    /api/v1/sedes/{sede_id}/config   Configuración completa
PATCH  /api/v1/sedes/{sede_id}/config   Actualiza configuración
```

### Zonas

```
GET    /api/v1/sedes/{sede_id}/zonas
POST   /api/v1/sedes/{sede_id}/zonas
GET    /api/v1/zonas/{zona_id}
PATCH  /api/v1/zonas/{zona_id}
DELETE /api/v1/zonas/{zona_id}
```

### Espacios

```
GET    /api/v1/sedes/{sede_id}/espacios           Lista con filtros
POST   /api/v1/sedes/{sede_id}/espacios           Crea bulk (max 100)
GET    /api/v1/espacios/{espacio_id}
PATCH  /api/v1/espacios/{espacio_id}
PUT    /api/v1/espacios/{espacio_id}/estado        Cambia estado
DELETE /api/v1/espacios/{espacio_id}

POST   /api/v1/sedes/{sede_id}/espacios/bulk
Body: { "espacios": [ { "numero": "A-001", "zona_id": "...", "tipo_vehiculo": "auto" }, ... ] }
```

### Dispositivos

```
GET    /api/v1/sedes/{sede_id}/dispositivos
POST   /api/v1/sedes/{sede_id}/dispositivos
GET    /api/v1/dispositivos/{dispositivo_id}
PATCH  /api/v1/dispositivos/{dispositivo_id}
DELETE /api/v1/dispositivos/{dispositivo_id}

GET    /api/v1/dispositivos/{dispositivo_id}/estado
POST   /api/v1/dispositivos/{dispositivo_id}/command  { "action": "open", "params": {} }
```

### Disponibilidad (real-time)

```
GET    /api/v1/sedes/{sede_id}/disponibilidad
Response: {
  "sede_id": "...",
  "total_espacios": 100,
  "libres": 45,
  "ocupados": 50,
  "mantenimiento": 5,
  "por_zona": [
    { "zona_id": "...", "zona": "P1", "libres": 20, "ocupados": 30 }
  ]
}

GET    /api/v1/sedes/{sede_id}/espacios/estado   Estado de todos los espacios
```

---

## Endpoints gRPC (interno)

```protobuf
service SedesService {
  rpc GetSede(GetSedeRequest) returns (Sede);
  rpc ListSedes(ListSedesRequest) returns (ListSedesResponse);
  rpc GetDisponibilidad(GetDisponibilidadRequest) returns (Disponibilidad);
  rpc UpdateEspacioEstado(UpdateEspacioEstadoRequest) returns (Espacio);
  rpc GetDispositivoEstado(GetDispositivoEstadoRequest) returns (DispositivoEstado);
}
```

---

## Gestión de Espacios por CSV

```
POST /api/v1/sedes/{sede_id}/espacios/import
Content-Type: multipart/form-data
file: csv con columns: numero, zona, tipo_vehiculo, tags

CSV format:
numero,zona,tipo_vehiculo,tags
A-001,P1,auto,"proximidad_entrada"
A-002,P1,auto,
B-001,P2,Moto,
```

Response:
```json
{
  "imported": 95,
  "errors": [
    { "row": 3, "numero": "A-003", "error": "Zona 'P9' no existe" }
  ]
}
```

---

## Configuración de Horarios

```json
{
  "horario_operacion": {
    "lunes": { "open": "06:00", "close": "22:00" },
    "martes": { "open": "06:00", "close": "22:00" },
    "miercoles": { "open": "06:00", "close": "22:00" },
    "jueves": { "open": "06:00", "close": "22:00" },
    "viernes": { "open": "06:00", "close": "22:00" },
    "sabado": { "open": "07:00", "close": "20:00" },
    "domingo": { "open": "08:00", "close": "18:00" },
    "festivos": { "open": "09:00", "close": "15:00" }
  },
  "cerrado_por_defecto": false
}
```

---

## Eventos Kafka

### Topic: `parkcore.sedes`

```json
{
  "event_type": "sede.created",
  "sede_id": "uuid",
  "tenant_id": "uuid",
  "timestamp": "2026-01-15T10:30:00Z",
  "data": { "nombre": "...", "codigo": "..." }
}
```

Eventos:
- `sede.created`, `sede.updated`, `sede.deleted`
- `zona.created`, `zona.updated`, `zona.deleted`
- `espacio.created`, `espacio.updated`, `espacio.estado_changed`
- `dispositivo.created`, `dispositivo.estado_changed`, `dispositivo.command_sent`

---

## Estados de Dispositivos

| Estado | Descripción | Timeout para offline |
|--------|-------------|---------------------|
| online | Conectado y respondiendo | - |
| offline | Sin comunicación > 5min | 5 min |
| error | Error de hardware o config | - |
| maintenance | En mantenimiento | - |

### Comandos a Dispositivos

```
Talanquera:
  - open: Abre la talanquera
  - close: Cierra la talanquera
  - reset: Reinicia el dispositivo

Cámara ANPR:
  - capture: Fuerza captura de imagen
  - recalibrate: Recalibra OCR
  - restart: Reinicia cámara
```

---

## Rate Limiting

- Lectura de disponibilidad: 60 rpm por sede
- Escritura (crear/actualizar): 30 rpm por sede
- Import bulk: 5 por hora por sede

---

## Dependencias

- **DB**: PostgreSQL `sedes` schema
- **Redis**: Cache de disponibilidad (TTL 5s para real-time)
- **Kafka**: Eventos de sede/dispositivo
- **Vault**: Secrets de configuración de dispositivos
- **Tenant-service**: Validación de límites de sede por plan

---

## Métricas

- `sedes_total{tenant_id, estado}`
- `espacios_total{sede_id, estado}`  -- estado: libre, ocupado, mantenimiento
- `dispositivos_online{sede_id, tipo}`
- `dispositivos_offline{sede_id, tipo}`
- `disponibilidad_refresh_duration_ms`

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "iot_gateway": "connected" }
GET /health/ready → verifica DB, Redis, y que IoT gateway responde
GET /health/live → solo proceso activo
```

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Eliminar sede con espacios ocupados | Error 400 "Hay espacios con vehículos actualmente" |
| Cambiar estado espacio a 'mantenimiento' ocupado | Error 400 "El espacio está ocupado, primero libere" |
| Crear espacio con número duplicado | Error 409 "Ya existe espacio con número {numero} en esta sede" |
| Dispositivo offline > 5min | Auto-marcar offline, publicar evento, alerta a operador |
| Zona con 0 espacios | Permitir pero mostrar warning |

---

## Notas

- Código de sede es único por tenant, no global
- Los espacios se numeran como "zona-numero" (ej: "P1-001")
- Cada sede tiene al menos una zona "General" por defecto
- La geolocalización (lat/long) se usa paraapp de cliente y reportes
- Dispositivos offline no bloquean operación de la sede
- Import CSV tiene modo "dry-run" para validar antes de apply