# Historias de Usuario

## Parqueadero — ParkCore

---

### 1. Consultar espacios disponibles

**Como** Cliente (conductor) **quiero** consultar espacios disponibles en una sede antes de llegar **para** planificar mi visita.

**Criterios de aceptación:**
- **Given** el cliente ha iniciado sesión en la app móvil
- **When** el cliente selecciona una sede y solicita disponibilidad
- **Then** el sistema muestra el número de espacios libres por zona con actualización en menos de 5 segundos

---

### 2. Lectura automática de placa a la entrada

**Como** Cliente (conductor) **quiero** que mi placa sea leída automáticamente a la entrada **para** no detenerme a interactuar con un operador.

**Criterios de aceptación:**
- **Given** un vehículo se aproxima a la entrada del parqueadero
- **When** la cámara ANPR captura la imagen de la placa
- **Then** el sistema registra la placa con timestamp y abre la talanquera sin intervención del cliente

---

### 3. Pago desde app móvil

**Como** Cliente (conductor) **quiero** pagar desde mi app móvil sin ir al cajero **para** ahorrar tiempo.

**Criterios de aceptación:**
- **Given** el cliente tiene un vehículo registrado dentro del parqueadero
- **When** inicia el pago desde la app y selecciona el método de pago
- **Then** el sistema confirma el pago, registra la transacción y habilita la salida del vehículo

---

### 4. Notificación de tiempo por vencer

**Como** Cliente (conductor) **quiero** recibir notificación cuando mi tiempo está por vencerse **para** renovar el pago oportunamente.

**Criterios de aceptación:**
- **Given** el cliente tiene un tiempo de permanencia activo
- **When** faltan 15 minutos para el vencimiento del tiempo pagado
- **Then** el sistema envía notificación push/SMS al cliente con opción de renovar desde la app

---

### 5. Ver espacios libres en tiempo real

**Como** Operador de parqueadero **quiero** ver en tiempo real cuántos espacios hay libres **para** orientar a los clientes.

**Criterios de aceptación:**
- **Given** el operador ha iniciado sesión en su panel de control
- **When** consulta la vista de ocupación de la sede
- **Then** el sistema muestra el conteo de espacios libres/ocupados por zona, actualizado en tiempo real

---

### 6. Apertura automática de talanquera tras pago

**Como** Operador de parqueadero **quiero** que la talanquera se abra automáticamente tras validar el pago **para** reducir mi intervención manual.

**Criterios de aceptación:**
- **Given** un cliente ha confirmado el pago desde la app
- **When** el vehículo se aproxima a la salida y el sistema valida el pago
- **Then** la talanquera se abre en menos de 1 segundo sin intervención del operador

---

### 7. Reportes de ingresos por período

**Como** Administrador de sede **quiero** consultar reportes de ingresos por día/semana/mes **para** tomar decisiones operativas.

**Criterios de aceptación:**
- **Given** el administrador tiene permisos de consulta sobre la sede
- **When** solicita un reporte de ingresos seleccionando el período (día/semana/mes)
- **Then** el sistema presenta los ingresos totales, cantidad de transacciones y comparativa con períodos anteriores

---

### 8. Bloqueo de placas de morosos

**Como** Administrador de sede **quiero** bloquear placas de morosos **para** evitar que salgan sin pagar.

**Criterios de aceptación:**
- **Given** existe un cliente con deuda pendiente registrada en el sistema
- **When** el vehículo con placa bloqueada intenta salir
- **Then** la talanquera permanece cerrada y se notifica al operador con los datos del moroso

---

### 9. Dashboard consolidado de KPIs por sede

**Como** Administrador global **quiero** ver KPIs consolidados de todas las sedes en un único dashboard **para** tener visibilidad de la red.

**Criterios de aceptación:**
- **Given** el administrador global tiene acceso a múltiples sedes
- **When** accede al dashboard consolidado
- **Then** el sistema muestra ingresos totales, ocupación promedio, transacciones y alertas cruzadas de todas las sedes

---

### 10. Precisión en lectura de placas mayor a 95%

**Como** Sistema (ANPR) **quiero** leer placas con precisión mayor a 95% **para** garantizar el flujo sin errores.

**Criterios de aceptación:**
- **Given** la cámara captura la imagen de una placa en condiciones normales de iluminación
- **When** el motor ANPR procesa la imagen
- **Then** la precisión de reconocimiento de caracteres es mayor al 95% y el resultado se devuelve en menos de 500ms

---

### 11. Registro de eventos de apertura en log inmutable

**Como** Sistema (ANPR) **quiero** registrar cada evento de apertura de talanquera en log inmutable **para** auditoría.

**Criterios de aceptación:**
- **Given** ocurre una apertura de talanquera (manual o automática)
- **When** el evento se dispara
- **Then** el sistema registra en un log inmutable: timestamp, placa, sede, tipo de apertura, usuario/actor que la detonó y resultado

---

### 12. Gestión de planes tarifarios

**Como** Administrador de sede **quiero** gestionar planes tarifarios (por hora, diario, mensual, flotas) **para** adaptar la oferta comercial.

**Criterios de aceptación:**
- **Given** el administrador de sede tiene permisos de configuración
- **When** crea, edita o elimina un plan tarifario
- **Then** el sistema aplica la tarifa correspondiente según el plan asociado al cliente o al tipo de vehículo

---
