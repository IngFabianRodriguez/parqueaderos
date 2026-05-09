# SPEC-03-012 — Facturación electrónica integrada con DIAN

## Metadata
- **RF origen**: RF-012
- **Módulo**: 03-crm-pagos
- **Prioridad**: Alta
- **Servicios**: billing-service, crm-service

---

## User Story
Como Operador o Cliente **quiero** recibir una factura electrónica validada por la DIAN por cada pago realizado **para** cumplir con la normativa colombiana de facturación y poder deducir impuestos.

## Objetivo
Generar documentos electrónicos de facturación (e-invoicing) completamente integrados con la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia), incluyendo: generación del XML-signed con firma digital, envío a la DIAN via Web Services, validación de rango de numeración autorizado, y distribución al comprador (email/PDF).

## Comportamiento Específico
### Happy Path (Facturación post-pago)
1. Pago confirmado en el sistema (RF-011)
2. Billing-service recibe evento `pago.completado`
3. Sistema obtiene datos del cliente (nombre, NIT/CC, dirección, email) y del tenant (razón social, NIT, régimen)
4. Sistema determina tipo de documento: factura electrónica (FE) o documento soporte (DS) según régimen del cliente
5. Sistema asigna siguiente número del rango configurado (atómico, evitar duplicados)
6. Sistema genera XML con estructura UBL 2.1 adaptada a Colombia
7. Sistema firma digitalmente el XML con certificado del tenant
8. Sistema envía XML a la DIAN via Web Service
9. Si aceptado: CUFE generado, estado → `validada`, PDF generado, email enviado
10. Si rechazado: estado → `rechazada`, operador notificado para corregir

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| DIAN no responde (>30s timeout) | Cola de reintento. Hasta 5 intentos con backoff exponencial. Luego alerta crítico al admin |
| NIT del comprador inválido | Se crea factura pero marcada `pendiente_validacion_nit` |
| Rango de numeración agotado | Sistema deja de emitir facturas. Alerta al admin |
| Cliente no tiene email | Se guarda PDF en el portal del cliente (app) sin envío de email |
| Factura duplicada (mismo pago re-facturado) | 409 con datos de factura ya existente |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| pago_id | UUID | Pago asociado a la factura | Sí |
| tipo_documento | VARCHAR | factura_electronica, documento_soporte | Sí |
| nit_comprador | VARCHAR | NIT o CC del cliente | Sí |
| razon_social | VARCHAR | Nombre o razón social | Sí |
| direccion | VARCHAR | Dirección de notificación | Sí |
| email | VARCHAR | Correo para envío de factura | Sí |
| regimen | VARCHAR | comumun, simplificado, responsable_iva | Sí |
| items | JSON | Array de líneas: descripción, cantidad, valor_unitario, iva, subtotal | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| factura_id | UUID | — |
| numero_factura | VARCHAR | Prefijo + número secuencial (ej: "FVE-001-000001") |
| cufe | VARCHAR | Código único de facturación electrónica (hash SHA384) |
| estado | VARCHAR | pendiente, validada, rechazada, revertida |
| pdf_url | VARCHAR | Link al PDF |
| xml_url | VARCHAR | Link al XML firmado |
| timestamp_emision | TIMESTAMP | — |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada pago exitoso genera una factura con número único del rango autorizado
2. Factura XML cumple estructura UBL 2.1 según normativa DIAN vigente
3. CUFE generado con algoritmo hash SHA384 obligatorio
4. Envío a DIAN con timeout < 30s, reintento automático si falla
5. PDF disponible dentro de 5 segundos después de validación DIAN
6. Nota crédito generada cuando hay reversión de pago

## Endpoints
- `POST /api/v1/facturas` — Crear factura (triggered por pago)
- `GET /api/v1/facturas/{factura_id}` — Detalle de factura
- `GET /api/v1/facturas/{factura_id}/pdf` — Descargar PDF
- `POST /api/v1/facturas/{factura_id}/nota-credito` — Generar nota crédito
- `GET /api/v1/facturas/por-cliente/{cliente_id}` — Historial de facturas del cliente

## Health Check
- `GET /health` → `{ "status": "ok", "service": "billing-service" }`

## Notas
- Normativa: Resolución DIAN 0012 de 2020 (sistema de facturación) y modificaciones posteriores.
- Para clientes del régimen comumun, se emite factura electrónica. Para no residentes o clientes sin NIT verificado, se emite documento soporte.
- Contingencia DIAN: cuando el servicio esté caído, se permite emitir facturas en modo contingencia con consecutivo propio, y se regulariza cuando el servicio vuelva.
- Firma digital requiere certificado SSL/OID de una autoridad certificadora autorizada (ANe, Certicámara, etc.).