# SPEC-08-083 — Configuración General (Nombre, Logo, Datos de Empresa)

## Metadata
- **RF origen**: RF-083
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: tenant-service, config-service

---

## User Story
**Como** administrador de un tenant **quiero** personalizar los datos de mi empresa (nombre, logo, dirección, NIT/tax ID) **para** que aparezca correctamente en facturas, reportes y correos automáticos que se envían a mis clientes.

## Objetivo
El sistema debe permitir al `tenant_admin` configurar los datos de su organización que aparecen en los documentos generados por el sistema: nombre legal, nombre comercial, logo, dirección, número fiscal/tributario, y contactos de soporte.

## Comportamiento Específico

### Datos configurables
1. `company_name`: Nombre legal de la empresa.
2. `trading_name`: Nombre comercial (puede diferir del legal).
3. `logo_url`: URL del logo (almacenado en S3).
4. `tax_id`: Número de identificación fiscal (NIT, RFC, CNPJ, etc.).
5. `address`: Dirección completa (calle, ciudad, estado, código postal, país).
6. `phone`: Teléfono de contacto.
7. `email`: Email de contacto principal.
8. `website`: Sitio web.
9. `support_contact`: Información de contacto de soporte.
10. `invoice_footer_text`: Texto adicional en el pie de factura.
11. `default_currency`: Moneda por defecto para transacciones.

### Almacenamiento
- Los datos se guardan en `tenants` y `tenants.settings`.
- El logo se sube a S3 y se almacena la URL en `tenants.logo_url`.
- Los cambios se publican como `TENANT_SETTINGS_UPDATED`.

### Aplicación en documentos
- Facturas: logo, nombre, tax_id, dirección.
- Emails de notificación: logo, nombre en el header.
- Reportes impresos: logo, nombre, fecha de generación.
- La app del cliente muestra el logo del tenant.

## Criterios de Aceptación
1. El admin puede configurar todos los datos de la empresa desde Settings → Organization.
2. El logo se sube como imagen (PNG/JPG) y se almacena en S3.
3. Los datos de la empresa aparecen en facturas, emails y reportes.
4. Los cambios en configuración se reflejan en el siguiente documento generado.
5. El `default_currency` se usa como referencia para nuevos sites si no se especifica.