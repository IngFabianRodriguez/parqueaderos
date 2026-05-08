# Requerimientos No Funcionales

## Parqueadero — ParkCore

---

## 1. Rendimiento

- Tiempo de respuesta de APIs < 200ms al percentil 95 en operaciones de consulta
- Tiempo de lectura ANPR < 500ms desde captura hasta resultado
- Apertura de talanquera < 1 segundo tras validación exitosa
- Dashboard con datos actualizados cada 5 segundos (WebSocket)

---

## 2. Disponibilidad (SLA)

- Uptime de 99.5% para APIs (excluyendo mantenimiento programado)
- Modo offline en sede: el sistema local debe poder operar independientemente por hasta 4 horas si se pierde conectividad con la nube
- Recuperación ante desastres: RPO < 1 hora, RTO < 4 horas

---

## 3. Escalabilidad

- Soportar hasta 50 sedes por instancia de plataforma
- Cada sede: hasta 500 espacios, 100 transacciones/hora pico
- Base de datos: hasta 10 millones de registros de transacciones/año por cliente

---

## 4. Seguridad

- TLS 1.3 en todas las comunicaciones
- AES-256 en reposo para datos sensibles (placas, información de pago)
- Cumplimiento con Ley 1581 de 2012 (protección de datos personales en Colombia)
- PCI-DSS si se procesan tarjetas de crédito/débito directamente

---

## 5. Mantenibilidad

- Código documentado con docstrings en español
- Cobertura de tests unitarios mínima: 80%
- Pipeline de CI que corre linter, tests y análisis estático en cada push

---

## 6. Compatibilidad

- Navegadores soportados: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Apps móviles: iOS 14+, Android 10+
- APIs: REST con formato JSON, documentación OpenAPI 3.0

---

## 7. Observabilidad

- Logs estructurados en formato JSON
- Métricas: Prometheus / Datadog
- Trazas distribuidas: OpenTelemetry
- Alertas automáticas ante errores críticos

---
