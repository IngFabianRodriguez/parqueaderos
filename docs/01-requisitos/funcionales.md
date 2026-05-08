# Requerimientos Funcionales

## Parqueadero — ParkCore SaaS

---

## Grupo 1: Módulo de Disponibilidad y Gestión de Sedes

**RF-001** | Disponibilidad | El sistema debe mostrar el conteo de espacios disponibles por sede en tiempo real (< 5 segundos de actualización) | Alta

**RF-002** | Disponibilidad | El sistema debe permitir consultar disponibilidad por zona dentro de una misma sede | Alta

**RF-003** | Disponibilidad | El sistema debe mantener historial de ocupación por hora para consultas históricas | Media

**RF-004** | Disponibilidad | El sistema debe permitir filtros de disponibilidad por tipo de espacio (cubierta, descubierta, VIP, moto) | Media

---

## Grupo 2: Módulo ANPR (Reconocimiento de Placas)

**RF-005** | ANPR | El sistema debe capturar la placa de un vehículo en el momento de entrada y registrar timestamp | Alta

**RF-006** | ANPR | El sistema debe buscar la placa a la salida, calcular duración y aplicar tarifa vigente | Alta

**RF-007** | ANPR | El sistema debe manejar el caso de placas ilegibles con registro manual por parte del operador | Alta

**RF-008** | ANPR | El sistema debe operar en modo offline si la conectividad se interrumpe, sincronizando al recuperar conexión | Alta

**RF-009** | ANPR | El sistema debe almacenar imágenes de cada captura con hash para auditoría | Media

---

## Grupo 3: Módulo CRM de Pagos y Cobros

**RF-010** | CRM/Pagos | El sistema debe registrar clientes (naturales y empresas) con sus placas asociadas | Alta

**RF-011** | CRM/Pagos | El sistema debe soportar múltiples métodos de pago: efectivo, PSE, tarjeta, Nequi, Daviplata | Alta

**RF-012** | CRM/Pagos | El sistema debe generar facturación electrónica integrada con DIAN | Alta

**RF-013** | CRM/Pagos | El sistema debe gestionar planes tarifarios: por minuto, por hora, diario, mensual, corporativo | Alta

**RF-014** | CRM/Pagos | El sistema debe enviar notificaciones push/SMS/email al cliente al entrar, al salir y ante pagos | Media

**RF-015** | CRM/Pagos | El sistema debe gestionar descuentos, cupones y programas de lealtad | Media

**RF-016** | CRM/Pagos | El sistema debe gestionar la cartera de morosos con bloqueo y desbloqueo de placas | Alta

**RF-017** | CRM/Pagos | El sistema debe soportar prepago (billetera virtual) con cargo y descuento automático | Media

---

## Grupo 4: Módulo de Control de Talanquera (IoT)

**RF-018** | Talanquera IoT | El sistema debe abrir la talanquera de salida solo si el pago está confirmado | Alta

**RF-019** | Talanquera IoT | El sistema debe permitir apertura manual por parte del operador en casos de emergencia | Alta

**RF-020** | Talanquera IoT | El sistema debe monitorear el estado de la talanquera (abierta/cerrada/error) en tiempo real | Alta

**RF-021** | Talanquera IoT | El sistema debe registrar cada comando enviado a la talanquera con timestamp, usuario y motivo | Alta

**RF-022** | Talanquera IoT | El sistema debe detectar falla de talanquera (no abre en 3s) y generar alerta inmediata | Alta

---

## Grupo 5: Módulo BI y Reportes

**RF-023** | BI/Reportes | El sistema debe generar reportes de ingresos, ocupación y tiempo promedio de estadía | Alta

**RF-024** | BI/Reportes | El sistema debe exportar datos a Excel/CSV y conectar con Power BI / Google Data Studio | Media

**RF-025** | BI/Reportes | El sistema debe generar reportes consolidados multi-sede para operadores con múltiples ubicaciones | Alta

---

## Grupo 6: Seguridad y Acceso

**RF-026** | Seguridad | El sistema debe autenticar usuarios con JWT y roles diferenciados (superadmin, admin_sede, operador, cliente) | Alta

**RF-027** | Seguridad | El sistema debe loguear todas las acciones sensibles en auditoría inmutable | Alta

**RF-028** | Seguridad | El sistema debe implementar RBAC: cada rol tiene permisos sobre recursos específicos | Alta

---

## Grupo 7: Gestión SaaS Multi-Tenant

### 7.1 Gestión de Tenants (Cuentas SaaS)

**RF-029** | SaaS | El sistema debe permitir crear una nueva cuenta tenant con datos básicos (nombre, email, empresa, NIT) | Alta

**RF-030** | SaaS | El sistema debe asignar un slug único a cada tenant (`/app/{slug}`) | Alta

**RF-031** | SaaS | El sistema debe iniciar cada nuevo tenant en un periodo de trial de 14 días sin cobro | Alta

**RF-032** | SaaS | El sistema debe convertir el trial en suscripción activa al confirmarse el primer pago | Alta

**RF-033** | SaaS | El sistema debe permitir que un tenant tenha múltiples usuarios propios (admin, managers, operadores) | Alta

**RF-034** | SaaS | El sistema debe aislar completamente los datos de cada tenant: ningún tenant puede ver datos de otro | Crítica

**RF-035** | SaaS | El sistema debe soportar la suspensión de un tenant por falta de pago (read-only) | Alta

**RF-036** | SaaS | El sistema debe soportar el churn (cancelación) de un tenant, reteniendo datos 90 días antes de eliminar | Media

---

### 7.2 Suscripciones y Facturación

**RF-037** | Billing | El sistema debe permitir seleccionar un plan de suscripción (Starter, Professional, Enterprise, Custom) | Alta

**RF-038** | Billing | El sistema debe cobrar automáticamente el plan mensual el día de renovación | Alta

**RF-039** | Billing | El sistema debe trackear uso excedente (transacciones, sedes extra, API calls) y facturarlo al cierre del ciclo | Alta

**RF-040** | Billing | El sistema debe procesar upgrades de plan con prorrateo inmediato | Alta

**RF-041** | Billing | El sistema debe procesar downgrades de plan al final del ciclo de facturación actual | Alta

**RF-042** | Billing | El sistema debe manejar reintentos de pago fallido (3 intentos en 7 días) antes de suspender | Alta

**RF-043** | Billing | El sistema debe generar invoices internos diferenciando suscripción base, excedentes y impuestos | Alta

**RF-044** | Billing | El sistema debe integralise con Stripe como motor de suscripciones y billing | Alta

**RF-045** | Billing | El sistema debe escuchar webhooks de Stripe para confirmar pagos, cambios de plan y cancelaciones | Alta

---

### 7.3 Branding y Personalización

**RF-046** | Branding | El sistema debe permitir que cada tenant configure su logo, color primario y secundario | Alta

**RF-047** | Branding | El sistema debe aplicar el branding del tenant en el dashboard de sus operadores | Alta

**RF-048** | Branding | El sistema debe aplicar el branding del tenant en los emails transacticionales (desde address, logo) | Alta

**RF-049** | Branding | El sistema debe permitir custom domain para tenants Enterprise+ (SSL automático) | Alta

**RF-050** | Branding | El sistema debe permitir white-label de la app móvil para tenants Custom | Media

---

### 7.4 API Keys y Acceso Externo

**RF-051** | API Keys | El sistema debe permitir que cada tenant genere API keys para integraciones de terceros | Alta

**RF-052** | API Keys | El sistema debe asociar scopes granulares a cada API key (`disponibilidad:read`, `reservas:write`, etc.) | Alta

**RF-053** | API Keys | El sistema debe aplicar rate limits por API key según el plan del tenant | Alta

**RF-054** | API Keys | El sistema debe permitir rotar y revocar API keys desde el dashboard | Alta

**RF-055** | API Keys | El sistema debe registrar el último uso de cada API key para auditoría | Media

---

### 7.5 Feature Flags por Plan

**RF-056** | Features | El sistema debe restringir features según el plan del tenant (multi-sede, BI, SSO, etc.) | Alta

**RF-057** | Features | El sistema debe mostrar error 403 cuando un tenant intenta acceder a feature no incluida en su plan | Alta

**RF-058** | Features | El sistema debe permitir añadir features a un plan existente vía upgrade | Alta

---

### 7.6 Onboarding de Nuevo Tenant

**RF-059** | Onboarding | El sistema debe guiar al nuevo usuario con un wizard de setup (datos empresa → primera sede → zona → talanquera → invitación equipo) | Alta

**RF-060** | Onboarding | El sistema debe enviar email de bienvenida con instrucciones de acceso al crear la cuenta | Alta

**RF-061** | Onboarding | El sistema debe verificar el email del usuario mediante OTP | Alta

**RF-062** | Onboarding | El sistema debe ofrecer asistente de configuración de primera sede con templates predefinidos | Media

---

### 7.7 Métricas SaaS

**RF-063** | Métricas SaaS | El sistema debe calcular y almacenar MRR (Monthly Recurring Revenue) por tenant por mes | Alta

**RF-064** | Métricas SaaS | El sistema debe calcular Churn Rate mensual (tenants perdidos / total al inicio del mes) | Alta

**RF-065** | Métricas SaaS | El sistema debe calcular NRR (Net Revenue Retention) mensual | Alta

**RF-066** | Métricas SaaS | El sistema debe trackear eventos significativos de suscripción (trial_started, converted, upgraded, churned, payment_failed) | Alta

---

### 7.8 SSO / SAML (Enterprise)

**RF-067** | SSO | El sistema debe permitir login via SAML 2.0 con IdP externos (Okta, Azure AD, Google Workspace) para tenants Enterprise | Alta

**RF-068** | SSO | El sistema debe hacer just-in-time provisioning: crear usuario en el tenant si el IdP lo autentica por primera vez | Alta

**RF-069** | SSO | El sistema debe mapear roles del IdP a roles internos del tenant según configuración | Media

---

### 7.9 Users Roles por Tenant

**RF-070** | Users | El sistema debe permitir crear usuarios dentro de un tenant con roles específicos | Alta

**RF-071** | Users | El sistema debe permitir que el tenant_admin asigne roles a usuarios de su organización | Alta

**RF-072** | Users | El sistema debe soportar MFA (autenticación de dos factores) para todos los usuarios | Alta

**RF-073** | Users | El sistema debe bloquear usuarios después de 5 intentos fallidos de login | Alta

**RF-074** | Users | El sistema debe permitir que un admin de tenant Restrinja el acceso de sus usuarios a sedes específicas | Alta

---

## Grupo 8: BI Avanzado (solo Enterprise+)

**RF-075** | BI | El sistema debe mostrar dashboard con tendencias de ocupación, ingresos y transacciones en tiempo real | Alta

**RF-076** | BI | El sistema debe comparar métricas entre sedes (benchmarking interno) | Alta

**RF-077** | BI | El sistema debe predecir demanda basándose en patrones históricos (forecasting de ocupación) | Media

**RF-078** | BI | El sistema debe exponer datos vía API GraphQL o REST para conexión con herramientas de BI externas | Media

---

## Grupo 9: Módulo B2B Flotas (Enterprise+)

**RF-079** | B2B | El sistema debe permitir registrar empresas con flotas de vehículos y asignarles un plan empresarial | Alta

**RF-080** | B2B | El sistema debe gestionar límites de gasto por vehículo dentro de una flota | Media

**RF-081** | B2B | El sistema debe generar facturación consolidada mensual por empresa con detalle por vehículo | Alta

**RF-082** | B2B | El sistema debe permitir que el admin de la empresa acceda a reportes de uso de su flota | Alta

---

*Total: 82 requerimientos funcionales*