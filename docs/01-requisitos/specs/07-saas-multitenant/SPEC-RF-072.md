# SPEC-07-072 — Autenticación de Dos Factores (MFA)

## Metadata
- **RF origen**: RF-072
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: auth-service, user-service

---

## User Story
**Como** administrador de un tenant **quiero** que todos los usuarios de mi organización puedan usar autenticación de dos factores (MFA) **para** agregar una capa extra de seguridad a sus cuentas y proteger contra accesos no autorizados.

## Objetivo
El sistema debe soportar MFA (Time-based One-Time Password) para todos los usuarios. El método por defecto es TOTP vía aplicaciones como Google Authenticator o Authy. El `tenant_admin` puede habilitar MFA obligatorio para todo su equipo.

## Comportamiento Específico

### Activación de MFA (usuario)
1. El usuario accede a `Settings → Security → Enable MFA`.
2. El sistema genera un secreto TOTP aleatorio (base32, 20 bytes) y lo almacena cifrado en `users.mfa_secret`.
3. El sistema genera el QR code con estructura `otpauth://totp/ParkCore:{email}?secret={secret}&issuer=ParkCore`.
4. El usuario escanea el QR con su app TOTP.
5. El sistema solicita un código de verificación de 6 dígitos.
6. El usuario ingresa el código; el sistema valida en ventana de ±1 timestep (30 segundos).
7. Si es correcto: `mfa_enabled = true`; se muestran 8 códigos de backup.

### Login con MFA obligatorio
1. Usuario ingresa email y password.
2. Sistema verifica password; si es incorrecto, retorna error.
3. Sistema solicita código TOTP.
4. Usuario ingresa código; sistema valida.
5. Si es válido: establece sesión. Si no: máximo 3 reintentos antes de bloqueo de 5 minutos.

### Deshabilitación de MFA
1. El usuario accede a `Settings → Security → Disable MFA`.
2. El sistema solicita password actual + código TOTP actual.
3. Si ambos son válidos: `mfa_enabled = false`; `mfa_secret` se elimina.

## Criterios de Aceptación
1. Todo usuario puede activar MFA usando cualquier app TOTP estándar.
2. El QR code se genera en formato estándar `otpauth://`.
3. Los códigos TOTP son válidos solo por 30 segundos; se acepta ±1 paso.
4. Cada código TOTP puede usarse solo una vez (protección contra replay).
5. El `tenant_admin` puede hacer obligatorio el uso de MFA.
6. El admin puede resetear el MFA de cualquier usuario de su organización.
7. Se generan 8 códigos de backup cuando se activa MFA.
8. El secreto TOTP se cifra con AES-256-GCM antes de almacenarse.