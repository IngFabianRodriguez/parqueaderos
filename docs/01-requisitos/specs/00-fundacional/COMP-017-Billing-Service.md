# COMP-017 — Billing Service

## Metadata

- **Nombre**: billing-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8017
- **DB**: PostgreSQL (schema `billing`)
- **Cache**: Redis
- **Servicios afectados**: payment-service, transaction-service, notification-service
- **Componentes relacionados**: payment-service, sedes-service, tenant-service, wallet-service

---

## Objetivo

Gestionar toda la lógica de facturación, tarifación y gestión de cartera del sistema de parqueo. Encargado de: cálculo de tarifas según planes configurados, generación de facturas electrónicas DIAN, gestión de cartera de morosos con bloqueo/desbloqueo de placas, procesamiento de wallets (prepago), y manejo de notas crédito/débito.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 15
- **Cache**: Redis (tarifas vigentes, configuración de planes, saldos wallet)
- **Message Broker**: Kafka (eventos de pago, facturación, morosos)
- **API**: REST + gRPC (interno)
- **XML**: xmlsec (firma digital), lxml (generación XML UBL)
- **DIAN**: Web Services (SOAP) para facturación electrónica

---

## Modelo de Datos

### Tabla: planes_tarifarios

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
sede_id             UUID FK → sedes (nullable)  -- null = todas
zona_id             UUID FK → zonas (nullable)  -- null = todas

nombre              VARCHAR(100) NOT NULL
tipo                VARCHAR(20) NOT NULL  -- minute, hour, day, monthly, corporate

frac_minima_minutos  INTEGER NOT NULL DEFAULT 60
frac_incremento_minutos INTEGER NOT NULL DEFAULT 15
precio_fraccion     DECIMAL(10,2) NOT NULL
precio_fraccion_adicional DECIMAL(10,2) NOT NULL

tope_maximo         DECIMAL(12,2)  -- Tarifa máxima por día/mes

multiplicador_hora_pico    DECIMAL(3,2) DEFAULT 1.0
hora_pico_inicio    TIME
hora_pico_fin       TIME

precio_nocturno     DECIMAL(10,2)
horario_nocturno_inicio TIME
horario_nocturno_fin   TIME

descuentos          JSONB DEFAULT '[]'  -- [{ "tipo": "corporate", "porcentaje": 10 }]

validez_desde       DATE NOT NULL
validez_hasta       DATE

activo              BOOLEAN DEFAULT true

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: facturas

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

numero_factura      VARCHAR(30) NOT NULL  -- Prefijo +secuencial (ej: FVE-001-000001)
serie               VARCHAR(20) NOT NULL  -- FVE, FES, etc.

pago_id             UUID FK → pagos NOT NULL

nit_comprador       VARCHAR(20) NOT NULL
razon_social         VARCHAR(255) NOT NULL
direccion            TEXT
email                VARCHAR(255)

regimen              VARCHAR(30) NOT NULL  -- comune, simplificado, responsable_iva

subtotal            DECIMAL(14,2) NOT NULL
monto_iva            DECIMAL(14,2) NOT NULL
monto_descuento      DECIMAL(14,2) DEFAULT 0
total               DECIMAL(14,2) NOT NULL

cufe                 VARCHAR(100)  -- Código único de facturación electrónica
qr_url              VARCHAR(500)

estado              VARCHAR(20) DEFAULT 'pendiente'  -- pendiente, validada, rechazada, revertida
fecha_validacion    TIMESTAMPTZ

pdf_url              VARCHAR(500)
xml_url              VARCHAR(500)

nota_credito_id     UUID FK → facturas (nullable)  -- si esta factura fue revertida

created_at           TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: detalle_factura

```sql
id                  UUID PK
factura_id          UUID FK → facturas NOT NULL

descripcion          TEXT NOT NULL
cantidad             DECIMAL(10,2) NOT NULL DEFAULT 1
valor_unitario       DECIMAL(14,2) NOT NULL
iva_porcentaje       INTEGER DEFAULT 19
iva_monto            DECIMAL(14,2) NOT NULL
subtotal             DECIMAL(14,2) NOT NULL
```

### Tabla: notas_credito

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

numero_nota          VARCHAR(30) NOT NULL
factura_id           UUID FK → facturas NOT NULL

nit_comprador        VARCHAR(20) NOT NULL
razon_social         VARCHAR(255) NOT NULL

concepto             TEXT NOT NULL
subtotal             DECIMAL(14,2) NOT NULL
iva_monto            DECIMAL(14,2) NOT NULL
total                DECIMAL(14,2) NOT NULL

cufe                 VARCHAR(100)
estado               VARCHAR(20) DEFAULT 'pendiente'

created_at           TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: rango_numeracion

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

serie               VARCHAR(20) NOT NULL  -- FVE, FES, NC
prefijo             VARCHAR(10) NOT NULL  -- FVE-001
numero_actual        BIGINT NOT NULL
numero_final         BIGINT NOT NULL

fecha_autorizacion   DATE
fecha_vencimiento    DATE

estado              VARCHAR(20) DEFAULT 'activo'  -- activo, agotado, cancelado

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: wallet

```sql
id                  UUID PK
cliente_id          UUID FK → clientes NOT NULL UNIQUE
tenant_id           UUID FK → tenants NOT NULL

saldo               DECIMAL(14,2) DEFAULT 0
saldo_disponible    DECIMAL(14,2) DEFAULT 0  -- Puede ser menor si hay holds

limite_saldo        DECIMAL(14,2) DEFAULT 500000  -- Max paraAML
umbral_alerta       DECIMAL(14,2) DEFAULT 20000  -- Alertar si saldo <

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: wallet_transaccion

```sql
id                  UUID PK
wallet_id           UUID FK → wallet NOT NULL
tenant_id           UUID FK → tenants NOT NULL

tipo                VARCHAR(20) NOT NULL  -- recarga, descuento, reversión, cargo_mensual
monto               DECIMAL(14,2) NOT NULL
saldo_anterior       DECIMAL(14,2) NOT NULL
saldo_nuevo          DECIMAL(14,2) NOT NULL

metodo_pago          VARCHAR(30)  -- pse, transferencia, efectivo, cargo_tarjeta

referencia_externa   VARCHAR(100)  -- ID en pasarela
idempotency_key      VARCHAR(100) UNIQUE

descripcion          TEXT

transaccion_ref_id   UUID  -- Referencia a transacción de parqueo si aplicafgs

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: morosos

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
cliente_id          UUID FK → clientes NOT NULL

placas_bloqueadas   VARCHAR(50)[] DEFAULT '{}'
monto_deuda         DECIMAL(14,2) NOT NULL
sesiones_pendientes  UUID[] DEFAULT '{}'

dias_mora            INTEGER DEFAULT 0

estado_bloqueo       VARCHAR(20) DEFAULT 'bloqueado'  -- bloqueado, observado, acuerdo_pago, desbloqueado

fecha_bloqueo        TIMESTAMPTZ
fecha_desbloqueo     TIMESTAMPTZ (nullable)

intentos_contacto   INTEGER DEFAULT 0

observaciones        TEXT

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: log_bloqueos

```sql
id                  UUID PK
moroso_id           UUID FK → morosos NOT NULL

accion              VARCHAR(30) NOT NULL  -- bloqueo, desbloqueo_pago, desbloqueo_manual
motivo              TEXT

usuario_id          UUID FK → usuarios (nullable)
ip_address          VARCHAR(45)

vehiculo_placa      VARCHAR(20)

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: configuracion_wallet

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

minimo_recarga      DECIMAL(10,2) DEFAULT 10000  -- $10,000 COP
maximo_saldo        DECIMAL(14,2) DEFAULT 500000
maximo_transaccion   DECIMAL(14,2) DEFAULT 200000

metodos_pago_permitidos VARCHAR(20)[] DEFAULT '["pse", "transferencia", "efectivo"]'

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints REST

### Tarifas

```
GET    /api/v1/tarifas/planes                    Lista planes tarifarios
POST   /api/v1/tarifas/planes                    Crear plan
GET    /api/v1/tarifas/planes/{id}               Detalle plan
PUT    /api/v1/tarifas/planes/{id}               Actualizar plan
DELETE /api/v1/tarifas/planes/{id}               Desactivar plan

GET    /api/v1/tarifas/calcular?sesion_id=X      Calcular precio sesión
GET    /api/v1/tarifas/calcular?placa=X&sede_id=Y&duracion_min=Z  Estimar precio
GET    /api/v1/tarifas/vigentes?sede_id=X        Planes activos para una sede
```

### Facturación

```
POST   /api/v1/facturas                          Crear factura (o triggered por pago)
GET    /api/v1/facturas/{id}                     Detalle factura
GET    /api/v1/facturas/{id}/pdf                 Descargar PDF
GET    /api/v1/facturas/{id}/xml                 Descargar XML
POST   /api/v1/facturas/{id}/nota-credito        Generar nota crédito
GET    /api/v1/facturas/por-cliente/{cliente_id} Historial cliente
GET    /api/v1/facturas/rangos                   Listar rangos numeración
POST   /api/v1/facturas/rangos                   Crear rango
GET    /api/v1/facturas/pendientes-validacion    Facturas esperando DIAN

POST   /api/v1/facturas/webhook/dian             Webhook respuesta DIAN
```

### Wallet

```
POST   /api/v1/wallet/recargar                   Recargar saldo
GET    /api/v1/wallet/saldo?cliente_id=X         Consultar saldo
GET    /api/v1/wallet/transacciones?cliente_id=X  Historial
POST   /api/v1/wallet/recargar/caja              Recarga en caja por operador
GET    /api/v1/wallet/alertas                    Estado de alertas

POST   /api/v1/wallet/descontar                  Descontar por pago (interno)
POST   /api/v1/wallet/reversar                    Reversar transacción
```

### Morosos

```
GET    /api/v1/morosos                           Lista morosos
GET    /api/v1/morosos/{id}                      Detalle moroso
POST   /api/v1/morosos/{id}/contacto             Registrar intento contacto
POST   /api/v1/morosos/{id}/desbloquear          Desbloquear (pago o manual)
PUT    /api/v1/morosos/politicas                 Configurar políticas bloqueo
GET    /api/v1/morosos/estadisticas              Métricas cartera

POST   /api/v1/morosos/{id}/acuerdo-pago         Registrar acuerdo de pago
GET    /api/v1/morosos/log-bloqueos?moroso_id=X   Historial de bloqueos
```

---

## Endpoints gRPC (interno)

```protobuf
service BillingService {
  rpc CalcularTarifa(CalcularTarifaRequest) returns (TarifaResponse);
  rpc ValidarPlacaBloqueada(PlacaRequest) returns (BloqueoResponse);
  rpc DescontarWallet(WalletDescontarRequest) returns (WalletResponse);
  rpc GetWalletCliente(ClienteRequest) returns (WalletInfo);
}
```

---

## Cálculo de Tarifa

```
1. Obtener plan de la zona o default
2. Calcular duración en minutos
3. Aplicar fracción mínima (redondear hacia arriba)
4. Aplicar precio por fracción
5. Si hora pico: aplicar multiplicador
6. Si horario nocturno: aplicar tarifa nocturna
7. Si excede tope: limitar al tope
8. Aplicar descuentos vigentes
9. Retornar precio final
```

### Ejemplo: Plan por hora ($3,000/hora, min 1hr, 15min adicionales)

- Cliente: 45 min → mínimo 60 min → $3,000
- Cliente: 90 min → 60 + 30 → $3,000 + $1,500 = $4,500
- Cliente: 3 horas → 3 × $3,000 = $9,000

---

## Eventos Kafka

### Topic: `parkcore.billing`

```json
{
  "event_type": "factura.validada",
  "factura_id": "uuid",
  "tenant_id": "uuid",
  "pago_id": "uuid",
  "cufe": "abc123...",
  "timestamp": "2026-05-08T10:00:00Z"
}
```

Eventos:
- `tarifa.calculada`
- `factura.creada`, `factura.validada`, `factura.rechazada`, `factura.revertida`
- `nota_credito.generada`, `nota_credito.validada`
- `wallet.recarga_procesada`, `wallet.descuento_aplicado`, `wallet.saldo_bajo`
- `moroso.bloqueado`, `moroso.desbloqueado`, `moroso.acuerdo_registrado`
- `bloqueo.placa_intento_salida` (cuando vehículo bloqueado intenta salir)

---

## Rate Limiting

- Consulta de tarifas: 100 rpm
- Crear factura: 20 rpm
- Recarga wallet: 10 rpm
- Consulta morosos: 30 rpm
- Bloqueo/desbloqueo: 30 rpm

---

## Dependencias

- **DB**: PostgreSQL `billing` schema
- **Redis**: Cache de planes tarifarios, saldos wallet
- **Kafka**: Eventos de facturación y morosos
- **Payment-service**: Datos de pagos que disparan facturación
- **Sedes-service**: Zonas y espacios para tarifación
- **Wallet-service**: Prepago (integrado en este servicio)
- **DIAN**: Web Services para facturación electrónica
- **S3**: Almacenamiento PDF/XML de facturas

---

## Métricas

- `billing_tarifa_calculations_total{tipo_plan}`
- `billing_facturas_generadas_total{estado, tipo}`
- `billing_factura_validation_duration_seconds`
- `billing_dian_success_rate`
- `wallet_saldo_actual{tenant_id}`
- `wallet_transacciones_total{tipo}`
- `wallet_saldo_bajo_alertas_total`
- `morosos_total{tenant_id, estado}`
- `moroso_bloqueos_total`
- `moroso_recuperacion_rate`
- `notas_credito_generadas_total`

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "dian": "available" }
GET /health/ready → verifica DB, Redis, y conexión DIAN
GET /health/live → solo proceso activo
```

---

## DIAN Integration

### Flujo Facturación Electrónica

```
1. Crear factura en BD con estado 'pendiente'
2. Generar XML UBL 2.1 con todos los campos requeridos
3. Firmar XML con certificado digital del tenant (XADES)
4. Enviar a DIAN via SOAP Web Service
5. Esperar respuesta (timeout 30s)
6. Si Acceptación: actualizar CUFE, estado='validada', generar PDF
7. Si Rechazo: estado='rechazada', guardar error
8. Si timeout: estado='pendiente', reintentar cada 5min
```

### Contingencia DIAN

- Si DIAN no responde por > 5min, activar modo contingencia
- Permite generar facturas con numeración propia (contingencia)
- Al restaurar, validar facturas en contingencia con batch

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|-----------------|
| Plan no configurado para zona | Usar tarifa fallback $50/min, alertar admin |
| Factura sin NIT válido | Crear como 'pendiente_validacion_nit' |
| Rango numeración agotado | Dejar de emitir, alertar admin |
| DIAN timeout | Reintentar 5 veces con backoff, luego marcar 'pendiente' |
| Wallet saldo insuficiente | No aplicar descuento, retornar error |
| Recarga duplicate idempotency | Retornar transacción original |
| Vehículo bloqueado intenta salir | Publicar evento, talanquera no abre |
| Acuerdo de pago incumplido | Volver a bloquear automáticamente |
| Reversión > 5 días DIAN | Generar nota débito en vez de crédito |

---

## Notas

- Moneda: COP (pesos colombianos), 2 decimales
- Tarifas se cachean en Redis por sede+zona+plan (TTL 1h)
- Wallet nunca puede tener saldo negativo
- Idempotency key para recargas: `{cliente_id}-{referencia}`
- Facturación electrónica: Resolución DIAN 0012 de 2020
- CUFE: SHA384 hash de {nit_emisor}+{num_factura}+{fecha}+{hora}+{valor}+{iva}+{dec_imps}
- Morosos: se bloquean si tienen sesiones > X días pendientes (configurable)
- Bloqueo es soft: impide salida por talanquera, no implica acción legal