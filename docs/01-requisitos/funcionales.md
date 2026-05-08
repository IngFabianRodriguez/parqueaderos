# Requerimientos Funcionales

## Parqueadero — ParkCore

---

**RF-001** | Disponibilidad | El sistema debe mostrar el conteo de espacios disponibles por sede en tiempo real (< 5 segundos de actualización) | Alta

**RF-002** | Disponibilidad | El sistema debe permitir consultar disponibilidad por zona dentro de una misma sede | Alta

**RF-003** | Disponibilidad | El sistema debe mantener historial de ocupación por hora para consultas históricas | Media

**RF-004** | ANPR | El sistema debe capturar la placa de un vehículo en el momento de entrada y registrar timestamp | Alta

**RF-005** | ANPR | El sistema debe buscar la placa a la salida, calcular duración y aplicar tarifa vigente | Alta

**RF-006** | ANPR | El sistema debe manejar el caso de placas ilegibles con registro manual por parte del operador | Alta

**RF-007** | ANPR | El sistema debe operar en modo offline si la conectividad se interrumpe, sincronizando al recuperar conexión | Alta

**RF-008** | CRM/Pagos | El sistema debe registrar clientes (naturales y empresas) con sus placas asociadas | Alta

**RF-009** | CRM/Pagos | El sistema debe soportar múltiples métodos de pago: efectivo, PSE, tarjeta, Nequi, Daviplata | Alta

**RF-010** | CRM/Pagos | El sistema debe generar facturación electrónica integrada con DIAN | Alta

**RF-011** | CRM/Pagos | El sistema debe gestionar planes tarifarios: por minuto, por hora, diario, mensual, corporativo | Alta

**RF-012** | CRM/Pagos | El sistema debe enviar notificaciones push/SMS/email al cliente al entrar, al salir y ante pagos | Media

**RF-013** | Talanquera IoT | El sistema debe abrir la talanquera de salida solo si el pago está confirmado | Alta

**RF-014** | Talanquera IoT | El sistema debe permitir apertura manual por parte del operador en casos de emergencia | Alta

**RF-015** | Talanquera IoT | El sistema debe monitorear el estado de la talanquera (abierta/cerrada/error) en tiempo real | Alta

**RF-016** | BI/Reportes | El sistema debe generar reportes de ingresos, ocupación y tiempo promedio de estadía | Alta

**RF-017** | BI/Reportes | El sistema debe exportar datos a Excel/CSV y conectar con Power BI / Google Data Studio | Media

**RF-018** | Seguridad | El sistema debe autenticar usuarios con JWT y roles diferenciados (superadmin, admin_sede, operador, cliente) | Alta

**RF-019** | Seguridad | El sistema debe loguear todas las acciones sensibles en auditoría inmutable | Alta

**RF-020** | Seguridad | El sistema debe implementar RBAC: cada rol tiene permisos sobre recursos específicos | Alta

---
