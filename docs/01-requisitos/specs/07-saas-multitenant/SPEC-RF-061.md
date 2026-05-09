# SPEC-07-061 — Verificación de Email del Usuario mediante OTP

## Metadata
- **RF origen**: RF-061
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: auth-service, notification-service, tenant-service

---

## User Story
**Como** nuevo usuario de ParkCore **quiero** verificar mi email para activar mi cuenta **para** confirmar que soy yo y poder comenzar a usar la plataforma de forma segura.

## Objetivo
El sistema debe enviar un código OTP (One-Time Password) de 6 dígitos al email del usuario al registrarse, y validar ese código antes de permitir que el usuario acceda a la plataforma. El OTP expira después de 10 minutos y solo puede usarse una vez.

## Comportamiento Específico

### Envío del OTP
1. El usuario se registra (RF-029) o el sistema detecta `status = pending_verification`
2. Sistema genera un OTP de 6 dígitos: `000000` - `999999`
3. Sistema almacena en Redis: `{user_id}_email_otp`, hash(otp), `expires_at = NOW() + 10 min`, `attempts = 0`
4. Sistema envía email con el OTP
5. Se genera evento `verification_otp_sent`

### Validación del OTP
1. El usuario ingresa el código de 6 dígitos en la interfaz de verificación
2. Sistema consulta `{user_id}_email_otp` en Redis
3. Se verifica: existencia, expiración (10 min), intentos (máx 3)
4. Se compara el OTP ingresado con el hash almacenado
5. En éxito: actualizar `users.email_verified_at = NOW()`, `status = active`
6. Generar evento `email_verified`
7. Redirigir al usuario al wizard de onboarding (RF-059)

### Reenvío de OTP
1. Si el usuario no recibe el email, puede hacer clic en "Reenviar código"
2. Sistema verifica que el OTP anterior haya expirado o que hayan pasado al menos 60 segundos
3. Se genera un nuevo OTP y se envía; el anterior se invalida

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| OTP incorrecto | Mostrar error "Código incorrecto. Te quedan X intentos." |
| OTP expiró | Mostrar "El código expiró. Solicita uno nuevo." |
| 3 intentos fallidos | El OTP expira; el usuario debe pedir reenvío |
| Email ya verificado | El usuario no ve la pantalla de verificación; va directo al dashboard |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El OTP se envía al email del usuario dentro de los 30 segundos posteriores al registro
2. El OTP expira después de 10 minutos
3. El usuario tiene máximo 3 intentos para ingresar el código correcto
4. La verificación exitosa marca `email_verified_at` y cambia `status` a `active`
5. El usuario no puede hacer login hasta verificar su email

## Endpoints
- `POST /api/v1/auth/verify-email` — Validar OTP de verificación
- `POST /api/v1/auth/resend-otp` — Reenviar OTP
- `GET /api/v1/auth/verification-status` — Consultar si el email ya está verificado

## Health Check
- `GET /health` → { "status": "ok" }
