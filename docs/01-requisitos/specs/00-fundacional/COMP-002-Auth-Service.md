# COMP-002 — Auth Service

## Metadata

- **Nombre**: auth-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8001
- **DB**: PostgreSQL (schema `auth`)
- **Servicios afectados**: API Gateway, todos los servicios

---

## Objetivo

Emitir y validar JWTs, gestionar sesiones de usuario, enforce RBAC, manejar MFA (TOTP), bloquear usuarios tras intentos fallidos, y registrar eventos de autenticación en auditoría.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0
- **DB**: PostgreSQL 15
- **Cache**: Redis (blacklist de tokens, sesión cache)
- **Auth**: JWT RS256 (access 15min, refresh 7 días)
- **Password**: bcrypt cost 12
- **MFA**: pyotp (TOTP 6 dígitos)

---

## Modelo de Datos

### Tabla: users

```
id              UUID PK
tenant_id       UUID FK → tenants (nullable para superadmin)
email           VARCHAR(255) NOT NULL UNIQUE
password_hash   VARCHAR(255) NOT NULL
nombre          VARCHAR(100) NOT NULL
rol             VARCHAR(50) NOT NULL  -- tenant_admin, sede_manager, operador, cliente, superadmin
sede_ids        UUID[] DEFAULT '{}'   -- vacío = todas las sedes
estado          VARCHAR(20) DEFAULT 'activo'  -- activo, inactivo, bloqueado
mfa_enabled     BOOLEAN DEFAULT false
mfa_secret      VARCHAR(255)          -- TOTP secret cifrado
intentos_fallidos INTEGER DEFAULT 0
bloqueado_hasta  TIMESTAMPTZ
ultimo_acceso   TIMESTAMPTZ
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: refresh_tokens

```
id              UUID PK
user_id         UUID FK → users
token_hash      VARCHAR(255) NOT NULL
familia         UUID NOT NULL  -- para detectar token theft
usado_en        TIMESTAMPTZ
expires_at      TIMESTAMPTZ NOT NULL
created_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: audit_auth

```
id              UUID PK
evento          VARCHAR(50) NOT NULL  -- login_success, login_failed, logout, mfa_enabled, blocked
user_id         UUID FK → users (nullable)
ip_address      VARCHAR(45)
user_agent      VARCHAR(500)
detalles        JSONB DEFAULT '{}'
created_at      TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints

### POST /api/v1/auth/login
**Request**:
```json
{
  "email": "string",
  "password": "string"
}
```
**Response 200**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": { "id", "email", "nombre", "rol", "tenant_id" }
}
```
**Errores**: 401 si credenciales inválidas, 423 si usuario bloqueado

### POST /api/v1/auth/refresh
**Request**:
```json
{
  "refresh_token": "eyJ..."
}
```

### POST /api/v1/auth/logout
**Headers**: `Authorization: Bearer <access_token>`
Invalida access token (blacklist en Redis TTL 15min) y marca refresh token como usado.

### POST /api/v1/auth/mfa/setup
Genera TOTP secret, retorna `otpauth://` URI para QR code.
Guarda `mfa_secret` cifrado en users.

### POST /api/v1/auth/mfa/verify
Valida código TOTP de 6 dígitos. Si válido, activa `mfa_enabled = true`.

### POST /api/v1/auth/validate
**Headers**: `Authorization: Bearer <token>`
Valida JWT sin hacer login. Retorna claims: `{user_id, rol, tenant_id, sede_ids, exp}`.

### GET /api/v1/auth/me
Retorna perfil completo del usuario autenticado.

### POST /api/v1/auth/password/reset
Envía email con enlace de reset (token one-time, expira 1h).

---

## Flujo de Login con MFA

```
1. POST /login → validate credentials (bcrypt)
2. Si mfa_enabled = true → retornar 403 con { require_mfa: true }
3. Generar access_token (15min) y refresh_token (7 días)
4. Guardar refresh_token con familia UUID
5. Registrar audit_auth (login_success)
6. Retornar tokens
```

**Si MFA requerido**:
```
7. POST /mfa/verify con { code: "123456" }
8. Validar TOTP (window ±1 step = 30 segundos)
9. Retornar access_token fresco
```

---

## Rate Limiting Auth

- Login: 5 intentos por IP por minuto → bloquear 15 min
- Refresh: 10 por minuto
- MFA verify: 5 por minuto

---

## Seguridad

- **Token theft detection**: Si un refresh_token se usa desde IP diferente, invalidar toda la familia (todos los refresh tokens de ese user_id)
- **Blacklist**: Access tokens revocados se guardan en Redis con TTL = tiempo restante del token
- **Bloqueo**: 5 intentos fallidos → `estado = bloqueado`, `bloqueado_hasta = NOW() + 15min`
- **Fail-Closed audit**: Todo evento de auth se registra antes de retornar respuesta

---

## Dependencias

- **DB**: PostgreSQL `auth` schema
- **Redis**: blacklist, cache de sesión
- **Vault**: secrets para JWT private key (para firmar)
- **Email**: notif-service para emails de reset

---

## Métricas

- `auth_login_total{status="success|failed"}`
- `auth_token_validation_duration_ms`
- `auth_mfa_setup_total`
- `auth_blocked_users_total`

---

## Health Check

`GET /health` → `{ "status": "ok", "db": "connected", "redis": "connected" }`
`GET /health/ready` → verifica DB y Redis
`GET /health/live` → solo que el proceso está corriendo