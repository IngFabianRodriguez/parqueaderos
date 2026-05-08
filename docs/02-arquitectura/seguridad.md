# Seguridad y Control de Acceso

---

## Modelo de Autenticación: JWT con Refresh Tokens

### Flujo Completo de Autenticación

```
┌────────┐                           ┌──────────────┐                      ┌────────────┐
│ Cliente│                           │ Auth Service │                      │   Redis    │
└───┬────┘                           └──────┬───────┘                      └─────┬──────┘
    │                                        │                                  │
    │  POST /auth/login (email, password)   │                                  │
    │ ─────────────────────────────────────> │                                  │
    │                                        │  Validar credenciales            │
    │                                        │ ─────────────────────────────────>│
    │                                        │                                  │
    │                                        │ <─ OK / Invalid ─────────────────│
    │                                        │                                  │
    │                                        │  Generar:                        │
    │                                        │  - access_token (JWT, 15min)     │
    │                                        │  - refresh_token (UUID, 7 días)  │
    │                                        │                                  │
    │                                        │  Guardar refresh_token en Redis  │
    │                                        │  (key: refresh:{uuid}, TTL 7d)   │
    │                                        │ ─────────────────────────────────>│
    │                                        │                                  │
    │  { access_token, refresh_token,       │                                  │
    │    expires_in: 900 }                   │                                  │
    │ <───────────────────────────────────── │                                  │
    │                                        │                                  │
    │  GET /api/resource (Authorization:     │                                  │
    │    Bearer {access_token})              │                                  │
    │ ─────────────────────────────────────> │                                  │
    │                                        │  Validar JWT (firma, expiry,     │
    │                                        │  claims)                         │
    │  200 OK / 401 Unauthorized             │                                  │
    │ <───────────────────────────────────── │                                  │
    │                                        │                                  │
    │  (access_token expirado)               │                                  │
    │  POST /auth/refresh                     │                                  │
    │  { refresh_token }                     │                                  │
    │ ─────────────────────────────────────> │                                  │
    │                                        │  Buscar refresh_token en Redis   │
    │                                        │ ─────────────────────────────────>│
    │                                        │                                  │
    │                                        │  ¿Existe y no revocado?          │
    │                                        │  ¿No excede max_usos?            │
    │                                        │                                  │
    │                                        │  Invalidar token anterior        │
    │                                        │  (delete key Redis)              │
    │                                        │ ─────────────────────────────────>│
    │                                        │                                  │
    │                                        │  Emitir nuevos tokens            │
    │  { access_token, refresh_token }       │                                  │
    │ <───────────────────────────────────── │                                  │
```

### Detalle de Tokens

**Access Token (JWT)**

- **Algoritmo**: RS256 (RSA Signature with SHA-256)
- **Contenido (claims)**:
  - `sub`: user_id (UUID)
  - `email`: email del usuario
  - `rol`: nombre del rol
  - `sede_id`: sede restringida (null si acceso global)
  - `tipo`: "access"
  - `iat`: issued at
  - `exp`: expiration (15 minutos desde emisión)
  - `jti`: JWT ID único para tracking

**Refresh Token**

- **Tipo**: UUID v4
- **Almacenamiento**: Redis con key `refresh:{uuid}` contendo `{user_id, created_at, user_agent, ip}`
- **TTL**: 7 días
- **Rotación**: Cada uso invalida el token anterior (refresh token rotation)
- **Límite**: Máximo 3 refresh consecutivos sin uso del access token (detección de theft)

### Revocación de Tokens

- **Logout**: Se elimina el refresh token de Redis. El access token sigue válido hasta su expiry natural (max 15 min).
- **Logout global (password change / security incident)**: Se añade el `jti` del access token a una blacklist en Redis (key `blacklist:{jti}`, TTL = tiempo restante del token).
- **Bloqueo de usuario**: Se eliminan todos los refresh tokens del usuario y se blacklistean sus access tokens activos.

---

## Modelo de Autorización: RBAC

### Definición de Roles

| Rol | Descripción | Ámbito |
|---|---|---|
| **superadmin** | Administrador total del sistema. Gestiona clientes enterprise, todas las sedes, configuración global, usuarios. | Todas las sedes y clientes |
| **admin_sede** | Administrador de una sede específica. Reportes, gestión tarifaria, bloqueo de placas, operadores. | Una sede asignada |
| **operador** | Personal en sede. Apertura manual de talanqueras, consulta de espacios, registro de pagos manuales, atención. | Una sede asignada |
| **cliente** | Usuario final a través de app. Consulta sus vehículos, historial de estadías, pagos, saldo prepago. | Solo sus propios datos |
| **api_client** | Aplicaciones terceras integradas (apps de mapas,.waze, plataformas de reserva). Solo APIs públicas. | Endpoints públicos |

---

## Permisos por Recurso

| Recurso | superadmin | admin_sede | operador | cliente | api_client |
|---|---|---|---|---|---|
| **sede** — crear | ✓ | ✗ | ✗ | ✗ | ✗ |
| **sede** — leer (todas) | ✓ | ✗ | ✗ | ✗ | ✗ |
| **sede** — leer (propia) | ✓ | ✓ | ✓ | ✗ | ✗ |
| **sede** — actualizar | ✓ | ✗ | ✗ | ✗ | ✗ |
| **sede** — eliminar | ✓ | ✗ | ✗ | ✗ | ✗ |
| **zona** — CRUD | ✓ | ✓ | ✗ | ✗ | ✗ |
| **espacio** — leer disponibilidad | ✓ | ✓ | ✓ | ✓ (mi sede) | ✓ (público) |
| **espacio** — actualizar estado | ✓ | ✓ | ✓ | ✗ | ✗ |
| **cliente** — crear | ✓ | ✓ | ✗ | ✗ | ✗ |
| **cliente** — leer (todos) | ✓ | ✓ (propia) | ✓ (propia) | ✗ | ✗ |
| **cliente** — leer (propio) | ✓ | ✓ | ✗ | ✓ | ✗ |
| **cliente enterprise** — gestionar | ✓ | ✗ | ✗ | ✗ | ✗ |
| **vehiculo** — crear/editar (propio) | ✓ | ✓ | ✗ | ✓ | ✗ |
| **vehiculo** — bloquear (placa) | ✓ | ✓ | ✗ | ✗ | ✗ |
| **registro_entrada** — crear | ✓ | ✓ | ✓ | ✗ | ✗ |
| **registro_entrada** — leer | ✓ | ✓ | ✓ | ✓ (propio) | ✗ |
| **registro_salida** — crear | ✓ | ✓ | ✓ | ✗ | ✗ |
| **registro_salida** — leer | ✓ | ✓ | ✓ | ✓ (propio) | ✗ |
| **pago** — crear | ✓ | ✓ | ✓ | ✓ (app) | ✗ |
| **pago** — leer (propio) | ✓ | ✓ | ✓ | ✓ | ✗ |
| **pago** — reportes | ✓ | ✓ | ✗ | ✗ | ✗ |
| **plan_tarifario** — CRUD | ✓ | ✓ | ✗ | ✗ | ✗ |
| **talanquera** — abrir (manual) | ✓ | ✓ | ✓ | ✗ | ✗ |
| **talanquera** — leer estado | ✓ | ✓ | ✓ | ✗ | ✓ (público) |
| **evento_iot** — leer | ✓ | ✓ (propia) | ✓ (propia) | ✗ | ✗ |
| **notificacion** — enviar | ✓ | ✓ | ✗ | ✗ | ✗ |
| **usuario** — crear | ✓ | ✓ (operador) | ✗ | ✗ | ✗ |
| **usuario** — gestionar (sede) | ✓ | ✓ | ✗ | ✗ | ✗ |
| **usuario** — leer roles | ✓ | ✓ | ✗ | ✗ | ✗ |
| **logs_auditoria** — leer | ✓ | ✓ | ✗ | ✗ | ✗ |
| **API pública** — disponibilidad | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## Cifrado

### Cifrado en Tránsito (TLS 1.3)

- **Comunicación cliente → servidor**: Todos los endpoints APIs Forces HSTS con TLS 1.3 mínimo. Cipher suites restringidas a AES-256-GCM, ChaCha20-Poly1305. Se rechaza向后兼容 con TLS 1.2 o inferior.
- **Comunicación entre microservicios**: mTLS (mutual TLS) con certificados emitidos por una CA interna (Vault PKI). Cada servicio tiene su propio certificado con CN correspondiente a su nombre de servicio.
- **MQTT IoT**: Los dispositivos IoT usan TLS sobre MQTT (port 8883). Certificados pre-configurados en fábrica o aprovisionados via IoT Fleet Manager.
- **Bases de datos**: Conexiones PostgreSQL y Redis usan TLS. Certificados de servidor validados contra CA interna o Let's Encrypt.
- **Certificados**: Let's Encrypt para APIs públicas. Vault PKI para infraestructura interna con rotación automática cada 90 días.

### Cifrado en Reposo (AES-256)

Los siguientes campos se cifran a nivel de aplicación usando AES-256-GCM antes de almacenarse en la base de datos:

| Campo | Tabla | Tipo de Dato Cifrado | Justificación |
|---|---|---|---|
| placa | vehiculo | Encrypted VARCHAR | Dato personal (Ley 1581), usado en ANPR |
| identificacion | cliente | Encrypted VARCHAR | Dato personal sensible |
| numero_tarjeta | pago (si se almacena) | Encrypted VARCHAR | PCI-DSS |
| cvv | pago | Encrypted VARCHAR | Nunca se almacena; solo en memoria durante transacción |
| password_hash | usuario | bcrypt (no AES, ya es hash) | Autenticación |

El keystore de claves AES se gestiona en HashiCorp Vault. Cada sede o tenant puede tener su propia DEK (Data Encryption Key) envelopada con una KEK (Key Encryption Key) maestra.

---

## Auditoría

### Log Inmutable de Eventos Sensibles

Los eventos sensibles se registran en una tabla append-only (`log_auditoria`) que no permite UPDATE ni DELETE a nivel de aplicación. La tabla resides en un esquema separado (`audit`) y solo es escribible vía funciones stored procedures con SECURITY DEFINER.

### Tabla de Eventos a Registrar

| ID Evento | Categoría | Descripción | Datos Registrados |
|---|---|---|---|
| AUTH_LOGIN_SUCCESS | autenticacion | Login exitoso | user_id, IP, user_agent, sede_id |
| AUTH_LOGIN_FAILURE | autenticacion | Login fallido | email, IP, user_agent, razon |
| AUTH_LOGOUT | autenticacion | Logout | user_id, IP |
| AUTH_TOKEN_REFRESH | autenticacion | Refresh de token | user_id, IP |
| AUTH_PASSWORD_CHANGE | autenticacion | Cambio de contraseña | user_id, IP |
| USER_CREATED | usuario | Usuario creado | user_id_creador, user_id_creado, rol_asignado |
| USER_UPDATED | usuario | Usuario modificado | user_id_editor, user_id_editado, campos_cambiados |
| USER_DISABLED | usuario | Usuario desactivado | user_id_ejecutor, user_id_desactivado |
| CLIENT_CREATED | cliente | Cliente creado | user_id, cliente_id, tipo |
| VEHICULO_BLOQUEADO | vehiculo | Vehículo bloqueado | user_id, vehiculo_id, placa, motivo |
| VEHICULO_DESBLOQUEADO | vehiculo | Vehículo desbloqueado | user_id, vehiculo_id |
| PAGO CREADO | pago | Pago registrado | user_id, pago_id, monto, forma_pago |
| PAGO_REEMBOLSADO | pago | Reembolso procesado | user_id, pago_id, monto |
| TALANQUERA_ABIERT A_MANUAL | talanquera | Apertura manual | user_id, talanquera_id, motivo |
| ESPACIO_BLOQUEADO | espacio | Espacio bloqueado | user_id, espacio_id, razon |
| CONFIG_CAMBIO | configuracion | Cambio en tarifa/zona | user_id, entidad, id, valores_previos |

### Estructura del Log de Auditoría

```sql
CREATE TABLE audit.log_auditoria (
    id              BIGSERIAL PRIMARY KEY,
    evento_id       VARCHAR(50) NOT NULL,
    categoria       VARCHAR(30) NOT NULL,
    usuario_id      UUID NOT NULL,
    usuario_email   VARCHAR(100),
    sede_id         UUID,
    recurso_tipo    VARCHAR(50),
    recurso_id      UUID,
    ip_address      INET,
    user_agent      TEXT,
    datos_previos   JSONB,
    datos_nuevos    JSONB,
    metadata        JSONB,
    timestamp       TIMESTAMPTZ DEFAULT NOW()
);
```

La tabla se particiona mensualmente. Particiones antiguas se comprimen con pg_compression y se mueven a almacenamiento frío (S3 Glacier o similar) después de 2 años.

---

## Rate Limiting

### Límites por Tipo de Cliente

| Tipo de Request | Límite | Ventana | Respuesta al Exceder |
|---|---|---|---|
| APIs autenticadas (por token) | 100 requests | 1 minuto | 429 Too Many Requests + Retry-After |
| APIs públicas (sin auth) | 20 requests | 1 minuto | 429 Too Many Requests |
| Login (por IP) | 5 intentos | 15 minutos | 429 + lockout 15 minutos |
| Login (por email) | 5 intentos | 15 minutos | 429 + lockout 15 minutos |
| Refresh token | 10 requests | 1 minuto | 401 Unauthorized |
| Webhooks entrantes (ANPR) | 1000 requests | 1 minuto | 429 |

### Implementación

El rate limiting se implementa usando un sliding window algorithm en Redis. Cada request incrementa un counter en `ratelimit:{tipo}:{identificador}` con TTL = ventana. La lógica vive en un middleware de API Gateway (Kong o custom) y en FastAPI via slowapi.

### Lockout de Login

Después de 5 intentos de login fallidos desde la misma IP o para el mismo email:
1. Se bloquea el acceso por 15 minutos.
2. Se Registra evento AUTH_LOGIN_FAILURE con bandera `lockout_triggered`.
3. Se envía notificación al usuario por canal disponible (email/sms) si está configurado.
4. El bloqueo se levanta automáticamente al completar el timeout o manualmente por un admin.

---

## Notas de Compliance

### Ley 1581 de 2012 (Colombia — Protección de Datos Personales)

- **Placas vehiculares** se clasifican como dato personal semipersonalizado (identifica un bien pero puede vincularse a una persona). Requirieren consentimiento del titular para su recolección y tratamiento.
- **Datos de identificación** (CC, nombre, email, teléfono) son datos personales ordinarios.
- **Medidas requeridas**:
  - Aviso de privacidad en app y puntos de recolección
  - Consentimiento explícito al registrar vehículo
  - Derecho de habeas data respetado via endpoint /privacidad
  - Registro deTreatment (RoT) en documentación interna
  - Encargado del tratamiento designado
- **Transferencia de datos a terceros**: Plate Recognizer recibe imágenes con placas; se suscribe DPA (Data Processing Agreement) con el proveedor garantizando que no retiene datos más allá del procesamiento.

### PCI-DSS (Payment Card Industry Data Security Standard)

Si se procesan pagos con tarjeta de crédito/débito directamente:

- **Scope**: Si ParkCore maneja terminal POS propia, está en scope PCI. Si usa pasarela de pago第三方 (Wompi, PayU, ePayco), el scope se reduce significativamente.
- **Si se procesa directamente**:
  - No almacenar PAN (número de tarjeta) — delegar tokenización a la pasarela
  - Si se almacenan tarjetas para pagos recurrentes (clientes enterprise), usar tokenización via Vault o plugin de la pasarela
  - Redes isoladas para sistemas de pago (segmentación)
  - Logs de auditoría en almacenamiento independiente
  - Evaluaciones de compliance trimestrales
- **Si se delega a pasarela**: Cumplimiento PCI del proveedor verificado (certificados AOC), auditoría anual.

### DIAN — Facturación Electrónica (Colombia)

- Los pagos en parqueadero pueden requerir factura electrónica si el cliente la solicita (persona jurídica principalmente).
- Se integra con la DIAN via un proveedor CV (Centro Virtual) autorizado o directamente via API de facturación.
- Los datos mínimos de factura: NIT del parqueadero, NIT/CC del cliente, detalle de servicios,羽毛, cuotas tributarias.
- Los campos de pago (monto, forma) deben reconciliarse con los registros de facturación para auditoría fiscal.
- Para clientes enterprise con muchos vehículos (flota), se facturan consolidaciones mensuales via nota Dérmica.
