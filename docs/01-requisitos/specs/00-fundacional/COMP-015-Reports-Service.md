# COMP-015 — Reports Service

## Metadata

- **Nombre**: reports-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8015
- **DB**: PostgreSQL (schema `reports`)
- **Cache**: Redis
- **Servicios afectados**: billing-service, transaction-service, soporte-service, analytics-service
- **Componentes relacionados**: billing-service, sedes-service, tenant-service

---

## Objetivo

Gestionar la generación, almacenamiento y distribución de reportes operativos y financieros. Provee acceso a reportes de ingresos, ocupación, tiempo promedio de estadía, reportes consolidados multi-sede, exportación a múltiples formatos (XLSX, CSV, PDF), conectores BI (OData para Power BI, JSON API para Google Data Studio), y programación de reportes periódicos con entrega por email.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 15
- **Cache**: Redis (cache de reportes generados, TTL 5min)
- **Message Broker**: Kafka (eventos de nuevos reportes, notificaciones)
- **Task Queue**: Celery + Redis (reportes async grandes)
- **API**: REST + OData (Power BI) + JSON (BI tools)
- **Librería Excel**: openpyxl (XLSX), pandas (agregación)
- **Scheduler**: Celery Beat (reportes programados)

---

## Modelo de Datos

### Tabla: report_templates

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

nombre              VARCHAR(255) NOT NULL
descripcion         TEXT
tipo                VARCHAR(30) NOT NULL  -- ingresos, ocupacion, tiempo_promedio, mixto, custom
categoria           VARCHAR(50)  -- operativo, financiero, ejecutivo

parametros_config   JSONB DEFAULT '{}'  -- parámetros default del template
filtros_disponibles JSONB DEFAULT '[]'  -- lista de filtros que acepta

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: report_schedules

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
template_id         UUID FK → report_templates

nombre              VARCHAR(255) NOT NULL
frecuencia          VARCHAR(20) NOT NULL  -- daily, weekly, monthly
hora_ejecucion      TIME NOT NULL
dia_mes             INTEGER  -- 1-28 para monthly
dia_semana          INTEGER  -- 0=Lunes, 6=Domingo para weekly

filtros             JSONB DEFAULT '{}'  -- filtros aplicados al generar

destinatarios       VARCHAR(255)[] NOT NULL  -- emails
formato_salida      VARCHAR(10) DEFAULT 'xlsx'  -- xlsx, csv, pdf

activo              BOOLEAN DEFAULT true
ultima_ejecucion    TIMESTAMPTZ
proxima_ejecucion   TIMESTAMPTZ

created_by          UUID FK → users
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: report_executions

```sql
id                  UUID PK
schedule_id         UUID FK → report_schedules (nullable)
tenant_id           UUID FK → tenants NOT NULL

nombre_reporte      VARCHAR(255)
tipo                VARCHAR(30)
filtros             JSONB DEFAULT '{}'

estado              VARCHAR(20) DEFAULT 'pending'  -- pending, running, completed, failed
archivo_url         VARCHAR(500)
tamano_bytes        INTEGER

fecha_inicio        DATE NOT NULL
fecha_fin           DATE NOT NULL

error_mensaje       TEXT

ejecutor_id         UUID FK → users
created_at          TIMESTAMPTZ DEFAULT NOW()
completed_at        TIMESTAMPTZ
```

### Tabla: report_delivery_log

```sql
id                  UUID PK
execution_id         UUID FK → report_executions NOT NULL
schedule_id         UUID FK → report_schedules (nullable)

destinatario        VARCHAR(255) NOT NULL
formato             VARCHAR(10)
tamano_bytes        INTEGER

estado              VARCHAR(20) DEFAULT 'pending'  -- pending, delivered, failed, retried
attempts            INTEGER DEFAULT 0
fecha_entrega       TIMESTAMPTZ
error_codigo        VARCHAR(50)
error_mensaje       TEXT

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: report_cache

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
hash_filtros        VARCHAR(64) NOT NULL  -- SHA256 de filtros

tipo                VARCHAR(30)
filtros             JSONB
data                JSONB
expires_at          TIMESTAMPTZ

created_at          TIMESTAMPTZ DEFAULT NOW()

UNIQUE(tenant_id, hash_filtros, tipo)
```

---

## Endpoints REST

### Reportes

```
GET    /api/v1/reports/templates              Lista templates disponibles
GET    /api/v1/reports/templates/{id}          Detalle de template
POST   /api/v1/reports/execute                Ejecutar reporte sincrónico
GET    /api/v1/reports/execute/{id}/status    Estado de ejecución async

GET    /api/v1/reports/ingresos               Reporte de ingresos
GET    /api/v1/reports/ocupacion              Reporte de ocupación
GET    /api/v1/reports/tiempo-promedio         Reporte tiempo promedio estadía
POST   /api/v1/reports/consolidated           Reporte multi-sede consolidado

GET    /api/v1/reports/executions             Historial de ejecuciones
GET    /api/v1/reports/executions/{id}        Detalle de ejecución
GET    /api/v1/reports/executions/{id}/download Descargar archivo
```

### Programación

```
GET    /api/v1/reports/schedules              Lista programas
POST   /api/v1/reports/schedules              Crear programa
GET    /api/v1/reports/schedules/{id}         Detalle de programa
PUT    /api/v1/reports/schedules/{id}         Actualizar programa
DELETE /api/v1/reports/schedules/{id}        Eliminar programa
POST   /api/v1/reports/schedules/{id}/pause   Pausar programa
POST   /api/v1/reports/schedules/{id}/resume  Reanudar programa

GET    /api/v1/reports/delivery-log           Log de entregas
GET    /api/v1/reports/delivery-log/export    Exportar log a CSV
```

### BI Connectors

```
GET    /api/v1/bi/reports/{tipo}              Endpoint JSON para Data Studio
GET    /odata/v1/transactions                 Endpoint OData para Power BI
GET    /odata/v1/tickets                       Endpoint OData tickets
GET    /odata/v1/spaces                       Endpoint OData espacios
```

---

## Endpoints OData (Power BI)

```protobuf
// Entidades disponibles
// /odata/v1/transactions - Transacciones de pago
// /odata/v1/tickets - Tickets de soporte
// /odata/v1/spaces - Espacios por sede

// Ejemplo de query OData:
// GET /odata/v1/transactions?$top=100&$skip=0&$filter=sede_id eq '{sede_id}'&$orderby=created_at desc
```

---

## Casos de Uso Principales

### 1. Generación de Reporte de Ingresos
```
1. Operador llama GET /api/v1/reports/ingresos?sede_id=X&fecha_inicio=2026-05-01&fecha_fin=2026-05-31
2. Service valida acceso a sede
3. Consulta transaction-service para transacciones cerradas en el período
4. Agrega por forma de pago y sede
5. Cachea resultado en Redis (TTL 5min)
6. Retorna JSON con totales y desglose
```

### 2. Exportación Async (>50k registros)
```
1. Operador llama POST /api/v1/exports con async=true
2. Service crea execution con estado 'pending'
3. Encola job Celery
4. Retorna 202 con job_id
5. Celery worker procesa, genera archivo
6. Archivo almacenado en S3 con URL temporal (24h)
7. Notification enviada al usuario
```

### 3. Reporte Multi-Sede
```
1. Admin multi-sede llama POST /api/v1/reports/consolidated
2. Service valida acceso a todas las sedes
3. Consulta en paralelo datos de cada sede
4. Calcula métricas consolidadas: total_ingresos, ocupacion_ponderada, ranking
5. Aplica comparativa con período anterior si se solicita
6. Retorna JSON con drill-down por sede
```

---

## Eventos Kafka

### Topic: `parkcore.reports`

```json
{
  "event_type": "report.executed",
  "execution_id": "uuid",
  "tenant_id": "uuid",
  "tipo": "ingresos",
  "estado": "completed",
  "timestamp": "2026-05-08T10:00:00Z",
  "registros": 1500
}
```

Eventos:
- `report.executed`, `report.failed`
- `report.schedule.triggered`, `report.schedule.completed`
- `report.delivered`, `report.delivery_failed`

---

## Rate Limiting

- Reportes under 30 días: 20 rpm por tenant
- Reportes over 30 días: 5 rpm por tenant
- Exportaciones async: 10 por hora por tenant
- BI connector requests: 100 rpm por token

---

## Dependencias

- **DB**: PostgreSQL `reports` schema
- **Redis**: Cache de reportes (TTL 5min), Celery broker
- **Kafka**: Eventos de reportes
- **Transaction-service**: Datos para reportes de ingresos
- **Billing-service**: Datos para reportes financieros
- **Sedes-service**: Metadatos de sedes para reportes multi-sede
- **S3**: Almacenamiento de archivos exportados

---

## Métricas

- `reports_generated_total{tipo, estado}`
- `report_generation_duration_seconds{tipo}`
- `report_export_size_bytes{tipo, formato}`
- `report_cache_hit_ratio`
- `report_schedules_active{tenant_id}`
- `report_delivery_success_rate`

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "celery": "ok" }
GET /health/ready → verifica DB, Redis, y broker de Celery
GET /health/live → solo proceso activo
```

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|-----------------|
| Rango de fechas > 90 días | Error 400 "Rango máximo: 90 días" |
| Usuario sin acceso a sede | 403 Forbidden |
| Exportación > 500k registros | Error "Volumen máximo 500k" |
| Redis no disponible | Fallback a consulta directa sin cache |
| Celery down | Reportes async fallan, sincónicos funcionan |
| BI token expirado | 401, re-autenticación requerida |
| Schedules conflictivos |Validación al crear, error si cruzan |

---

## Notas

- Reportes se cachean por combinación de filtros + tenant para evitar regenerar los mismos
- Exportaciones async van a S3-compatible storage, URL expires en 24h
- OData implementa $top, $skip, $filter, $orderby
- Row-level security aplica en todos los endpoints BI
- Scheduler usa Celery Beat con timezone del tenant
- Materialized views pre-agregan datos nightly para加速 reportes grandes