# SPEC-08-086 — Categorías de Vehículos (Autos, Motos, Camiones, Discapacitados)

## Metadata
- **RF origen**: RF-086
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: config-service, vehicle-service, rate-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar las categorías de vehículos que acepta mi estacionamiento **para** que el sistema aplique las tarifas correctas según el tipo de vehículo y respete las restricciones de acceso.

## Objetivo
El sistema debe permitir al `tenant_admin` definir las categorías de vehículos que operan en cada sede. Cada categoría tiene: nombre, código, descripción, si requiere permisos especiales, y si tiene restricciones de acceso. Las categorías se usan para filtrar tarifas y controlar el ingreso.

## Comportamiento Específico

### Categorías predefinidas (seed)
El sistema viene con categorías por defecto:
- `car`: Automóvil estándar.
- `motorcycle`: Motocicleta.
- `truck`: Camión o vehículo de carga.
- `bicycle`: Bicicleta.
- `disabled`: Vehículo para personas con discapacidad (espacios reservados).
- `electric`: Vehículo eléctrico (zona de carga, si aplica).
- `service`: Vehículos de servicio (delivery, taxi, etc.).

### Configuración por sede
1. El admin accede a `Settings → Sites → [Sede] → Vehicle Categories`.
2. Ve las categorías habilitadas para la sede.
3. Puede habilitar/deshabilitar categorías y configurar por sede:
   - `enabled`: booleano.
   - `max_capacity`: número máximo de espacios para esta categoría (null = ilimitado).
   - `requires_permission`: booleano — si necesita registro previo para acceder.
   - `allowed_vehicle_types`: tipos específicos de vehículo que aplican.

### Categorías personalizadas
1. El admin puede crear categorías adicionales con:
   - `category_code`: identificador único (ej: "van", "bus").
   - `category_name`: nombre visible (ej: "Van / Microbús").
   - `description`: descripción.
   - `icon`: icono para la UI.

### Aplicación en control de acceso
- Si una categoría tiene `max_capacity` y se alcanzó, el sistema deniega el ingreso de vehículos de esa categoría.
- Si `requires_permission = true`, el vehículo debe estar pre-registrado para poder ingresar.

## Criterios de Aceptación
1. El admin puede habilitar/deshabilitar categorías de vehículos por sede.
2. Cada categoría puede tener un límite de capacidad específico por sede.
3. Algunas categorías pueden requerir registro previo (permiso).
4. El sistema deniega ingresos si la capacidad de una categoría está llena.
5. Las categorías personalizadas se pueden crear además de las predefinidas.
6. Las categorías se usan para filtrar tarifas (RF-085).