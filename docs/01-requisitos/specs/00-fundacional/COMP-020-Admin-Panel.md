# COMP-020 — Admin Panel (Web)

## Metadata

- **Nombre**: Admin Panel (Tenant Admin + Superadmin)
- **Tipo**: Aplicación Web
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los servicios de backend

---

## Objetivo

Panel de administración web para que tenant_admins y superadmins configuren y operen el sistema. Es la herramienta principal de gestión — configurar sedes, usuarios, tarifas, dispositivos, ver reportes y métricas.

---

## Stack Tecnológico

- **Framework**: Angular 21 (standalone components, signals)
- **UI Library**: PrimeNG 21 (Apple-like diseño)
- **Styling**: SCSS con CSS custom properties para theming (dark/light)
- **State Management**: NgRx Signals (para estado complejo), Angular Signals para estado local
- **HTTP**: Angular HttpClient con interceptors (auth, error handling)
- **WebSocket**: @stomp/stompjs (RxJS wrapper)
- **Forms**: Reactive Forms + Zod validation
- **Charts**: PrimeNG Charts (Chart.js wrapper) + D3 para visualizaciones avanzadas
- **PDF**: pdfmake para exportación de reportes
- **CI/CD**: GitHub Actions + Angular CLI Docker

---

## Arquitectura de Componentes

```
src/app/
├── core/                    # Singleton services, guards, interceptors
│   ├── auth/               # AuthService, AuthGuard, RoleGuard
│   ├── services/           # API services (ApiService genérico)
│   ├── interceptors/        # AuthInterceptor, ErrorInterceptor
│   └── models/             # Interfaces TypeScript de todos los modelos
├── shared/                  # Componentes y directives reutilizables
│   ├── components/         # DataTable, Chart, Modal, etc.
│   ├── directives/         # PermissionDirective, LoadingDirective
│   └── pipes/              # CurrencyCOP, TimeAgo, PlacaFormat
├── features/
│   ├── dashboard/          # Dashboard principal (widgets configurables)
│   ├── sedes/              # CRUD sedes, zonas, espacios
│   ├── usuarios/           # Gestión de usuarios y roles
│   ├── dispositivos/       # Talanqueras, ANPR, sensores
│   ├── tarifas/            # Planes tarifarios, fracciones, promociones
│   ├── clientes/           # CRM, morosos, flotas
│   ├── reportes/           # Generador de reportes, exportador
│   ├── billing/            # Suscripción, invoices, métodos de pago
│   ├── configuracion/     # Settings tenant, branding, webhooks
│   └── soporte/            # Tickets, chat, métricas NPS
└── layouts/
    ├── admin-layout/       # Shell con sidebar + topbar (glassmorphism)
    └── auth-layout/         # Login, register, forgot password
```

---

## Theming (Dark/Light)

```scss
// Light mode (default Apple-like)
--surface-ground: #f5f5f7;
--surface-card: #ffffff;
--surface-section: #ffffff;
--text-color: #1d1d1f;
--primary-color: #0071e3;
--accent-color: #34c759;

// Dark mode
--surface-ground: #000000;
--surface-card: #1d1d1f;
--surface-section: #2d2d2d;
--text-color: #f5f5f7;
--primary-color: #0a84ff;
--accent-color: #30d158;
```

Toggle en topbar → persiste en localStorage → Apply y observa el shell completo (sidebar, cards, modals, charts).

---

## Páginas y Funcionalidades

### Dashboard (RF-159 — parte del Admin Panel)

Widgets configurables (drag & drop):
- Espacios disponibles / tasa ocupación (gráfico donut)
- Ingresos del día / vs ayer (gráfico línea)
- Alertas activas (lista con badges)
- Dispositivos offline (contador con link)
- Transacciones últimas 24h (tabla compacta)

### Gestión de Sedes (RF-154)

```
/admin/sedes                    → Lista de sedes con búsqueda
/admin/sedes/nueva             → Formulario creación
/admin/sedes/{id}              → Detalle + tabs
/admin/sedes/{id}/zonas         → CRUD zonas
/admin/sedes/{id}/espacios      → Grid de espacios (estado visual)
/admin/sedes/{id}/dispositivos  → Talanqueras + ANPR + estado
/admin/sedes/{id}/config        → Configuración específica
```

### Gestión de Usuarios (RF-151, RF-152)

```
/admin/usuarios                 → DataTable con filtros
/admin/usuarios/nuevo          → Formulario + selector de rol
/admin/usuarios/{id}           → Editar, desactivar, reset password
/admin/roles                   → CRUD roles con permisos (matriz)
```

### Gestión de Dispositivos (RF-158)

```
/admin/dispositivos            → Mapa de calor de estado por sede
/admin/dispositivos/{id}       → Logs de comandos, latency, heartbeat
/admin/dispositivos/{id}/config → Configuración específica
```

### Tarifas y Promociones (RF-161, RF-162, RF-163)

```
/admin/tarifas                 → DataTable de planes
/admin/tarifas/nueva           → Constructor visual de tarifa
/admin/promociones             → CRUD cupones y descuentos
```

### Reportes (RF-116 a RF-130)

```
/admin/reportes                → Selector de tipo de reporte
/admin/reportes/ingresos       → Filtros + gráficos + exportación
/admin/reportes/ocupacion      → Heatmap + tendencia
/admin/reportes/morosidad      → Lista + acciones de cobro
/admin/reportes/operador       → KPIs por operador
/admin/reportes/programados    → scheduler de reportes email
```

### Billing (RF-154, RF-155, RF-156)

```
/admin/billing                 → Suscripción actual, plan, renovate date
/admin/billing/invoices        → Lista de invoices con descarga PDF
/admin/billing/metodos-pago    → Stripe Customer Portal redirect
/admin/billing/upgrade         → Checkout Stripe
```

### Configuración (RF-083 a RF-099)

```
/admin/configuracion           → Secciones: general, branding, webhooks, notif
/admin/configuracion/branding  → Logo upload, colores, custom domain
/admin/configuracion/webhooks → CRUD + test webhook
/admin/configuracion/notif     → Templates email/SMS/push
```

### Soporte (RF-175 a RF-180)

```
/admin/soporte/tickets         → Kanban: open | in_progress | resolved
/admin/soporte/nps             → Dashboard NPS + calificaciones
/admin/soporte/chat            → Chat en tiempo real con clientes
```

---

## Componentes Shared Más Usados

| Componente | Descripción |
|------------|-------------|
| `DataTableComponent` | Wrapper de PrimeNG Table con filtros, sorting, pagination, export |
| `ChartWidgetComponent` | Wrapper de PrimeNG Chart con loading state y error handling |
| `ConfirmDialogComponent` | Modal de confirmación con cuerpo personalizable |
| `StatusBadgeComponent` | Badge con color según estado (verde/amarillo/rojo/gris) |
| `LoadingOverlayComponent` | Spinner con mensaje personalizable |
| `PermissionDirective` | `*appHasPermission="'edit'"` — oculta element si no tiene permiso |
| `CurrencyCOPPipe` | `{{ amount \| currencyCOP }}` → `$45.000 COP` |
| `TimeAgoPipe` | `{{ date \| timeAgo }}` → `hace 5 minutos` |
| `PlacaFormatPipe` | `{{ placa \| placaFormat }}` → `ABC-123` con uppercase automático |

---

## Modelo de Estado (NgRx Signals)

```typescript
// Auth state
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

// Sedes state
interface SedesState {
  sedes: Sede[];
  selectedSede: Sede | null;
  loading: boolean;
  error: string | null;
}

// Notification state (toasts)
interface NotificationState {
  toasts: Toast[];
}
```

---

## Guards y Resolvers

| Guard/Resolver | Propósito |
|----------------|-----------|
| `AuthGuard` | Redirige a /login si no autenticado |
| `RoleGuard` | Redirige a /403 si rol no autorizado |
| `TenantGuard` | Verifica que el usuario pertenece al tenant |
| `SedeResolver` | Precarga datos de sede antes de cargar ruta |
| `ReportResolver` | Precarga datos para reportes pesados |

---

## Interceptors

```typescript
// AuthInterceptor: inyecta Bearer token en cada request
// ErrorInterceptor: captura 401 → refresh → retry; captura 4xx → toast
// TenantInterceptor: inyecta header X-Tenant-Id en cada request
```

---

## Endpoints Consumidos

```
GET    /api/v1/tenants/{tenant_id}
GET    /api/v1/sedes
POST   /api/v1/sedes
GET    /api/v1/sedes/{id}
PUT    /api/v1/sedes/{id}
DELETE /api/v1/sedes/{id}
GET    /api/v1/sedes/{id}/zonas
POST   /api/v1/sedes/{id}/zonas
GET    /api/v1/sedes/{id}/espacios
PUT    /api/v1/sedes/{id}/espacios/{espacio_id}
GET    /api/v1/usuarios
POST   /api/v1/usuarios
PUT    /api/v1/usuarios/{id}
DELETE /api/v1/usuarios/{id}
GET    /api/v1/dispositivos
GET    /api/v1/dispositivos/{id}/estado
POST   /api/v1/dispositivos/{id}/comando
GET    /api/v1/tarifas
POST   /api/v1/tarifas
GET    /api/v1/reportes/ingresos
GET    /api/v1/reportes/ocupacion
GET    /api/v1/reportes/morosidad
GET    /api/v1/reportes/operador
POST   /api/v1/reportes/exportar
GET    /api/v1/audit-log
WS     /ws/admin/actualizaciones
```

---

## Dark/Light Mode Implementation

```typescript
// ThemeService
private readonly _prefersDark = signal(
  window.matchMedia('(prefers-color-scheme: dark)').matches
);

public readonly theme = computed(() => this._prefersDark() ? 'dark' : 'light');

toggle(): void {
  this._prefersDark.set(!this._prefersDark());
  document.documentElement.setAttribute('data-theme', this.theme());
  localStorage.setItem('theme', this.theme());
}
```

Persistencia: `localStorage.getItem('theme')` → si existe, usar ese; si no, detectar `prefers-color-scheme`.

---

## Performance

- Lazy loading para cada feature module (`loadChildren`)
- OnPush change detection en todos los componentes
- Virtual scrolling para DataTables con > 100 rows
- Skeleton loaders en vez de spinners para contenido
- Preconnect a fonts.googleapis.com y APIs del backend

---

## Dependencias

- **Backend**: API Gateway → todos los microservicios
- **Charts**: PrimeNG Charts, D3.js
- **PDF**: pdfmake
- **Maps**: Google Maps SDK (para ubicación de sedes)
- **Notifications**: Servicio de toasts integrado en core

---

## Métricas

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Bundle size (initial): < 500KB gzipped
- Lighthouse Performance: > 90
- Accessibility: WCAG 2.1 AA