# Referencia de APIs y Endpoints

## Códigos de Error Comunes

| Código | Descripción              |
|--------|--------------------------|
| 400    | Solicitud inválida       |
| 401    | No autenticado           |
| 403    | Prohibido                |
| 404    | No encontrado            |
| 500    | Error interno del servidor |

### Formato de Error

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error",
    "details": {}
  }
}
```

---

## Módulo: Auth

### POST `/api/v1/auth/login`

**Request body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "rol": "admin"
  }
}
```

**Descripción:** Autentica usuario y retorna tokens JWT

### POST `/api/v1/auth/refresh`

**Request body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "expires_in": 3600
}
```

**Descripción:** Refresca el token de acceso usando el refresh token

### POST `/api/v1/auth/logout`

**Descripción:** Invalida la sesión del usuario

---

## Módulo: Sedes

### GET `/api/v1/sedes`

**Response:**
```json
{
  "sedes": [
    {
      "id": "uuid",
      "nombre": "Sede Centro",
      "direccion": "Calle 123",
      "capacidad_total": 100,
      "capacidad_disponible": 45
    }
  ]
}
```

**Descripción:** Lista todas las sedes

### GET `/api/v1/sedes/{id}`

**Response:**
```json
{
  "id": "uuid",
  "nombre": "Sede Centro",
  "direccion": "Calle 123",
  "capacidad_total": 100,
  "capacidad_disponible": 45
}
```

**Descripción:** Obtiene detalles de una sede específica

### POST `/api/v1/sedes`

**Request body:**
```json
{
  "nombre": "Sede Norte",
  "direccion": "Av. Principal 456",
  "capacidad_total": 150
}
```

**Descripción:** Crea una nueva sede

### PUT `/api/v1/sedes/{id}`

**Request body:**
```json
{
  "nombre": "Sede Norte Actualizada",
  "direccion": "Av. Principal 456",
  "capacidad_total": 200
}
```

**Descripción:** Actualiza una sede existente

---

## Módulo: Disponibilidad

### GET `/api/v1/sedes/{id}/disponibilidad`

**Response:**
```json
{
  "sede_id": "uuid",
  "capacidad_total": 100,
  "capacidad_disponible": 45,
  "porcentaje_ocupacion": 55,
  "timestamp": "2026-05-08T00:00:00Z"
}
```

**Descripción:** Obtiene disponibilidad en tiempo real de una sede

### GET `/api/v1/sedes/{id}/disponibilidad/historial`

**Response:**
```json
{
  "historial": [
    {
      "fecha": "2026-05-07",
      "capacidad_promedio": 72.5,
      "porcentaje_ocupacion_promedio": 27.5
    }
  ]
}
```

**Descripción:** Obtiene historial de disponibilidad de una sede

---

## Módulo: ANPR

### POST `/api/v1/anpr/captura`

**Request body:**
```json
{
  "sede_id": "uuid",
  "placa": "ABC123",
  "timestamp": "2026-05-08T00:00:00Z",
  "imagen_base64": "..."
}
```

**Descripción:** Webhook receives plate capture from camera

### GET `/api/v1/anpr/registro/{placa}`

**Response:**
```json
{
  "placa": "ABC123",
  "ultimo_ingreso": "2026-05-08T00:00:00Z",
  "ultima_sede": "Sede Centro",
  "vehiculo": {
    "marca": "Toyota",
    "modelo": "Corolla",
    "color": "Negro"
  }
}
```

**Descripción:** Busca registro por placa

---

## Módulo: Pagos

### POST `/api/v1/pagos`

**Request body:**
```json
{
  "cliente_id": "uuid",
  "sede_id": "uuid",
  "monto": 15000,
  "metodo_pago": "wompi"
}
```

**Response:**
```json
{
  "id": "uuid",
  "estado": "pendiente",
  "enlace_pago": "https://wompi.co/pago/..."
}
```

**Descripción:** Crea una nueva transacción de pago

### POST `/api/v1/pagos/{id}/confirmar`

**Descripción:** Webhook de confirmación desde pasarela de pago

### GET `/api/v1/pagos/{id}`

**Response:**
```json
{
  "id": "uuid",
  "cliente_id": "uuid",
  "sede_id": "uuid",
  "monto": 15000,
  "estado": "completado",
  "timestamp": "2026-05-08T00:00:00Z"
}
```

**Descripción:** Obtiene estado de un pago

---

## Módulo: Talanquera

### POST `/api/v1/talanquera/{id}/abrir`

**Request body:**
```json
{
  "autorizado_por": "uuid",
  "motivo": "ingreso"
}
```

**Descripción:** Abre la talanquera de forma remota

### GET `/api/v1/talanquera/{id}/estado`

**Response:**
```json
{
  "id": "uuid",
  "estado": "cerrada",
  "ultima_apertura": "2026-05-08T00:00:00Z",
  "sede_id": "uuid"
}
```

**Descripción:** Obtiene estado actual de la talanquera

---

## Módulo: Clientes

### GET `/api/v1/clientes`

**Response:**
```json
{
  "clientes": [
    {
      "id": "uuid",
      "nombre": "Juan Pérez",
      "email": "juan@ejemplo.com",
      "telefono": "+573001234567"
    }
  ]
}
```

**Descripción:** Lista todos los clientes

### POST `/api/v1/clientes`

**Request body:**
```json
{
  "nombre": "María García",
  "email": "maria@ejemplo.com",
  "telefono": "+573009876543"
}
```

**Descripción:** Crea un nuevo cliente

### GET `/api/v1/clientes/{id}/vehiculos`

**Response:**
```json
{
  "vehiculos": [
    {
      "id": "uuid",
      "placa": "XYZ789",
      "marca": "Honda",
      "modelo": "Civic",
      "color": "Gris"
    }
  ]
}
```

**Descripción:** Lista vehículos asociados a un cliente

### GET `/api/v1/clientes/{id}/historial`

**Response:**
```json
{
  "historial": [
    {
      "fecha": "2026-05-07",
      "sede": "Sede Centro",
      "tiempo_minutos": 120,
      "monto_pagado": 10000
    }
  ]
}
```

**Descripción:** Obtiene historial de ingresos de un cliente

---

## Módulo: Reportes

### GET `/api/v1/reportes/ingresos`

**Query params:** `fecha_inicio`, `fecha_fin`, `sede_id` (opcional)

**Response:**
```json
{
  "total_ingresos": 1500000,
  "cantidad_transacciones": 150,
  "ingresos_por_dia": [
    {
      "fecha": "2026-05-07",
      "monto": 500000
    }
  ]
}
```

**Descripción:** Genera reporte de ingresos en un periodo

### GET `/api/v1/reportes/ocupacion`

**Query params:** `sede_id`, `fecha`

**Response:**
```json
{
  "sede_id": "uuid",
  "fecha": "2026-05-07",
  "porcentaje_ocupacion_promedio": 65.5,
  "hora_pico": "09:00",
  "horas_bajo_ocupacion": ["03:00", "04:00", "05:00"]
}
```

**Descripción:** Reporte de ocupación por sede

### GET `/api/v1/reportes/tiempos-promedio`

**Query params:** `sede_id` (opcional)

**Response:**
```json
{
  "tiempo_promedio_minutos": 45.5,
  "tiempo_maximo_minutos": 180,
  "tiempo_minimo_minutos": 10,
  "por_sede": [
    {
      "sede_id": "uuid",
      "tiempo_promedio": 42.3
    }
  ]
}
```

**Descripción:** Reporte de tiempos promedio de estadía

---

## WebSocket

### WS `/api/v1/ws/disponibilidad/{sede_id}`

**Descripción:** Conexión WebSocket para actualizaciones en tiempo real de disponibilidad

**Mensaje recibido:**
```json
{
  "tipo": "actualizacion_disponibilidad",
  "sede_id": "uuid",
  "capacidad_disponible": 44,
  "timestamp": "2026-05-08T00:00:00Z"
}
```

**Descripción:** Recibe actualizaciones en tiempo real cuando la disponibilidad de espacios cambia
