# SPEC-07-saas-multitenant-067 — El sistema debe permitir autenticación via SAML 2

## Metadata
- **RF origen**: RF-067
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de un tenant Enterprise **quiero** que mis usuarios puedan iniciar sesión con sus credenciales corporativas (Okta, Azure AD, Google Workspace) **para** eliminar la necesidad de记忆 nuevas contraseñas y garantizar compliance con las políticas de seguridad de su empresa. ---

## Objetivo
El sistema debe permitir autenticación via SAML 2.0 para tenants del plan Enterprise. El flujo incluye: redirección al IdP seleccionado, recepción del assertion de SAML, validación de firma y atributos, creación de sesión en ParkCore. La configuración del IdP (metadata XML, URLs de SSO) es específica por tenant y se gestiona desde el admin panel. ---

## Comportamiento Específico

### Happy Path
1. El usuario accede a `GET /auth/login` y selecciona "SSO Enterprise" (si el tenant tiene SSO habilitado). 2. El usuario es redirigido a `GET /auth/saml/{tenant_slug}/login` donde se selecciona el IdP configurado. 3. ParkCore construye el AuthnRequest de SAML 2.0 y firma la petición con el certificado privado del tenant. 4. El usuario es redirigido (302) al endpoint de SSO del IdP con el AuthnRequest codificado en Base64 como `SAMLRequest`. 5. El IdP presenta su página de login al usuario (si no tiene sesión activa). 6. El usuario se autentica con credenciales corporativas. 7. El IdP responde con un redirect (302) a `POST /auth/saml/{tenant_slug}/acs` (Assertion Consumer Service) con el `SAMLResponse` codificado. 8. El auth-service: a. Recibe el `SAMLResponse`. b. Extrae el certificado público del IdP desde la configuración guardada del tenant. c. Verifica la firma del SAML Response usando el certificado del IdP. d. Valida: `NotBefore`, `NotOnOrAfter`, `Audience`, `Destination`. e. Extrae atributos: `NameID` (identificador único), `email`, `first_name`, `last_name`, `groups` (si aplica). 9. Con el `NameID` o `email`, busca el usuario en `users`. 10. Si el usuario no existe y está habilitado el JIT provisioning (RF-068), lo crea. 11. Actualiza `last_login` del usuario. 12. Genera un JWT de sesión con `user_id`, `tenant_id`, `roles`. 13. Redirige al usuario a `GET /auth/saml/{tenant_slug}/callback?token=<jwt>` o establece cookie. 14. El cliente almacena el token y accede a los endpoints de la API. ### Flujo deLogout (SLO - Single Logout) 1. Usuario hace clic en "Cerrar sesión". 2. Se envía `GET /auth/saml/{tenant_slug}/logout`. 3. ParkCore genera un `LogoutRequest` y redirige al IdP. 4. El IdP procesa el logout y responde con `LogoutResponse`. 5. ParkCore invalida la sesión local. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | session_token | string | JWT de sesión | | user_id | uuid | ID del usuario en ParkCore | | tenant_id | uuid | ID del tenant | | expires_at | timestamp | Expiración del token | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | session_token | string | JWT de sesión | | user_id | uuid | ID del usuario en ParkCore | | tenant_id | uuid | ID del tenant | | expires_at | timestamp | Expiración del token | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Tenants Enterprise pueden configurar múltiples IdPs (Okta, Azure AD, Google Workspace). 2. El flujo de autenticación SSO sigue el estándar SAML 2.0 sin deviations. 3. La firma del SAML Response se verifica usando el certificado público del IdP almacenado. 4. Los atributos `NameID` y `email` se extraen correctamente de todos los IdPs soportados. 5. Si el usuario no existe y JIT provisioning está habilitado (RF-068), se crea automáticamente. 6. El usuario recibe una sesión válida en ParkCore después del flujo SSO. 7. El logout del sistema localiza al IdP para Single Logout (SLO) si el IdP lo soporta. 8. El flujo SSO es transparente para el usuario cuando ya tiene sesión activa en el IdP. ---

## Endpoints
- `GET /auth/login` — Página de login con opción SSO - `GET /auth/saml/{tenant_slug}/login` — Inicio del flujo SAML (redirige al IdP) - `POST /auth/saml/{tenant_slug}/acs` — Assertion Consumer Service (recibe SAML Response) - `GET /auth/saml/{tenant_slug}/logout` — Cierre de sesión SSO - `GET /auth/saml/{tenant_slug}/sls` — Single Logout Service (recibe LogoutResponse del IdP) - `GET /api/v1/admin/sso/config` — Consulta de configuración SSO del tenant - `PUT /api/v1/admin/sso/config` — Actualización de configuración SSO del tenant ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se debe guardar la configuración de cada IdP incluyendo: `entity_id`, `sso_url`, `slo_url`, `x509_certificate` (público), `metadata_xml`. - Los certificados deben renovarse antes de su expiración; el admin panel debe mostrar warnings 30 días antes. - Para testing local, se puede usar el sandbox de Okta/Azure con una aplicación de test. - El flujo SAML requiere que el servidor tenga acceso a los endpoints del IdP; configurar apropiadamente en entornos con proxy. - Si el IdP soporta assertions encriptadas, el sistema debe poder descifrar usando la clave privada del tenant. - No se almacenan contraseñas de los usuarios SSO — toda la autenticación es manejada por el IdP.
