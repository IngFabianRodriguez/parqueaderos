# SPEC-07-080 — Retención de Datos por Jurisdicción

## Metadata
- **RF origen**: RF-080
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: tenant-service, data-retention-service, audit-service

---

## User Story
**Como** administrador de un tenant **quiero** que el sistema respete las políticas de retención de datos de mi jurisdicción **para** cumplir con las regulaciones de protección de datos aplicables (GDPR, LGPD, etc.).

## Objetivo
El sistema debe aplicar políticas de retención de datos configurables por jurisdicción. Los datos personales de usuarios y vehículos se anonimizan o eliminan según las reglas definidas una vez transcurrido el período de retención. Las políticas se aplican automáticamente via jobs programados.

## Comportamiento Específico

### Políticas de retención configurables
Cada tenant define su política de retención via `data_retention_policies`:
- `jurisdiction`: GDPR, LGPD, CCPA, Custom
- `user_data_retention_days`: días antes de anonimizar datos de usuarios (default: 730)
- `vehicle_data_retention_days`: días antes de anonimizar datos de vehículos (default: 365)
- `transaction_data_retention_days`: días antes de архивировать transacciones (default: 2555 / 7 años)
- `audit_log_retention_days`: días antes de eliminar logs (default: 730)
- `include_anonymization`: booleano — true = anonimizar, false = eliminar

### Aplicación de políticas (job nocturno)
1. El job `data-retention-processor` se ejecuta diariamente a las 3:00 AM UTC.
2. Consulta las políticas activas de cada tenant.
3. Para cada tenant, identifica registros fuera del período de retención.
4. Si `include_anonymization = true`:
   - Users: reemplaza PII con `ANONYMIZED_{hash}`; elimina email, phone.
   - Vehicles: elimina `owner_name`, `owner_document`; mantiene plate.
   - Transactions: se архивируют en tabla separate, no se eliminan.
5. Si `include_anonymization = false`: elimina físicamente los registros.
6. Se registra cada aplicación de política en `data_retention_log`.

## Criterios de Aceptación
1. Cada tenant puede configurar políticas de retención según su jurisdicción.
2. El sistema aplica las políticas automáticamente via job nocturno.
3. Los datos fuera de retención se anonimizan o eliminan según configuración.
4. Los registros financieros (transactions) nunca se eliminan; solo se архивируют.
5. Cada aplicación de política genera un log en `data_retention_log`.
6. El `superadmin` puede definir políticas por defecto para nuevos tenants.
7. Los usuarios pueden solicitar eliminación de sus datos (right to erasure) manualmente.