# COMP-019 — Mobile Apps (Operator & Client)

## Metadata

- **Nombre**: App Operador + App Cliente
- **Tipo**: Aplicaciones Móviles
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los servicios de backend

---

## Objetivo

Proveer aplicaciones móviles nativas (iOS/Android) para dos usuarios: operadores del parqueadero (App Operador) y clientes conductores (App Cliente). Ambas apps se comunican exclusivamente con el API Gateway, consumiendo los microservicios del backend.

---

## Stack Tecnológico

- **Framework**: Flutter 3.x (iOS 14+, Android 8+)
- **State Management**: Riverpod 2.x
- **HTTP Client**: Dio con interceptors automáticos de auth
- **WebSocket**: socket_io_client (para tiempo real)
- **Local Storage**: Hive (offline cache)
- **Push Notifications**: firebase_messaging (FCM) + apple_push_notification (APNS)
- **Analytics**: Firebase Analytics + Crashlytics
- **CI/CD**: Codemagic (iOS), GitHub Actions (Android)

---

## App Operador

### Funcionalidades Core

| RF | Funcionalidad | Descripción |
|----|--------------|-------------|
| RF-131 | Dashboard operador | Espacios disponibles, ocupación, ingresos del día |
| RF-132 | Selector de sede | Cambio rápido entre sedes multisede |
| RF-133 | Registro manual entrada | Placa, fecha/hora, observación |
| RF-134 | Registro manual salida | Cálculo de valor a pagar |
| RF-135 | Registro de pago | Efectivo, transferencia, Nequi, Daviplata |
| RF-136 | Control talanquera | Apertura/cierre con doble tap |
| RF-137 | Estado talanquera real-time | WebSocket: abierta/cerrada/error/offline |
| RF-138 | Notificaciones push | Mora, talanquera offline, alerta |
| RF-139 | Resolución alertas | Resolver/descartar alertas, historial 24h |
| RF-140 | Búsqueda cliente | Por placa/nombre/teléfono + historial |
| RF-141 | Bloqueo vehículo | Bloqueo/desbloqueo con contraseña |

### Modelo de Datos Local (Hive)

```dart
// Operador
Box<Operador>: { id, nombre, rol, sede_ids[], token, refresh_token }

// Cache de sede
Box<SedeCache>: { id, nombre, zonas[], dispositivos[] }

// Cache de espacios
Box<EspaciosCache>: { sede_id, espacios[], last_update }

// Cola offline
Box<OfflineQueue>: [ { tipo, payload, timestamp } ]
```

### Endpoints Consumidos

```
GET  /api/v1/sedes/{sede_id}/disponibilidad
GET  /api/v1/sedes/{sede_id}/dashboard
POST /api/v1/operador/registro/entrada
POST /api/v1/operador/registro/salida
POST /api/v1/operador/pago
POST /api/v1/operador/talanquera/{id}/comando
GET  /api/v1/operador/clientes/buscar?q=
POST /api/v1/operador/vehiculos/{id}/bloquear
WS   /ws/operador/sede/{sede_id}
```

### Flujo Offline

1. Si hay conexión → sincronizar inmediatamente
2. Si no hay conexión → guardar en `OfflineQueue` (Hive)
3. Al reconectar → procesar cola en orden FIFO
4. Si el servidor rechaza (409 Conflict) → marcar para revisión manual

---

## App Cliente

### Funcionalidades Core

| RF | Funcionalidad | Descripción |
|----|--------------|-------------|
| RF-142 | Ver espacios disponibles | Tiempo real por sede y zona |
| RF-143 | Prepago | Selección duración, pago anticipado |
| RF-144 | Recordatorio + renovación | Push al vencer, renovar desde app |
| RF-145 | Gestionar vehículos | Agregar/editar/eliminar hasta 5 |
| RF-146 | Métodos de pago | Tarjeta, Nequi, Daviplata + default |
| RF-147 | Historial transacciones | Filtros + exportar PDF/CSV |
| RF-148 | Facturas electrónicas | Ver y descargar |
| RF-149 | Config notificaciones | Por canal (push/SMS/email) |
| RF-150 | Promociones | Descuentos personalizados |

### Modelo de Datos Local (Hive)

```dart
// Cliente
Box<Cliente>: { id, email, nombre, vehiculos[], metodos_pago[], preferencia_notif }

// Vehículos
Box<VehiculoCache>: [ { id, placa, tipo, marca, modelo, color } ]

// Métodos de pago
Box<MetodosPago>: [ { id, tipo, ultimos_digitos, es_default } ]

// Historial
Box<HistorialCache>: { transacciones[], last_sync }

// Cola offline
Box<OfflineQueue>: [ { tipo, payload, timestamp } ]
```

### Endpoints Consumidos

```
GET  /api/v1/clientes/me
GET  /api/v1/clientes/me/vehiculos
POST /api/v1/clientes/me/vehiculos
PUT  /api/v1/clientes/me/vehiculos/{id}
DELETE /api/v1/clientes/me/vehiculos/{id}
GET  /api/v1/sedes/{sede_id}/disponibilidad
POST /api/v1/clientes/prepago
POST /api/v1/clientes/renovar
GET  /api/v1/clientes/me/transacciones
GET  /api/v1/clientes/me/facturas
PUT  /api/v1/clientes/me/notificaciones
WS   /ws/clientes/sede/{sede_id}
```

### Flujo de Prepago

```
1. Cliente selecciona sede y zona
2. Cliente elige duración (15min - 24h)
3. App muestra monto calculado (tarifa × duración)
4. Cliente selecciona método de pago
5. App crea Payment Intent (POST /api/v1/clientes/prepago)
6. App procesa pago con pasarela (Stripe/Nequi)
7. Si OK → crear registro de prepago en backend
8. Backend envía push confirmando inicio de parqueo
9. Si tiempo vence → backend envía recordatorio push
10. Cliente puede renovar (vuelve al paso 3)
```

---

## Seguridad

- **Certificates**: SSL pinning en ambos platforms
- **Biometric Auth**: Face ID / Touch ID para login (opcional)
- **Token Storage**: SecureStorage (iOS Keychain, Android EncryptedSharedPreferences)
- **Offline Data**: Hive encryption con clave derivada del auth token
- **API Calls**: Todas por HTTPS, JWT en header Authorization

---

## Métricas

- Crash-free sessions: > 99.5%
- App launch time: < 2s cold start
- API response time (P95): < 1s
- Offline queue processing: automatic, < 30s post-reconnect
- Push delivery rate: > 95%

---

## Dependencias

- **Backend**: API Gateway, todos los servicios
- **Push**: FCM (Android), APNS (iOS)
- **Maps**: Google Maps SDK (para selector de sede en mapa)
- **Payments**: Stripe SDK (tarjetas), Open Banking APIs (Nequi/Daviplata)

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| Sin internet al registrar entrada | Guardar localmente, sync cuando reconnect |
| Pago en proceso pero app cierra | Verificar estado en backend al reabrir, retry si necesario |
| Token expirado durante operación | Interceptar 401, hacer refresh automático, reintentar request |
| Prepago vence mientras offline | Al reconectar, detectar y mostrar modal de renovación |
| Placa no reconocida a salida | Operator hace registro manual, se vincula al pago existente |