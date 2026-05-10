# SPEC-08-091 — Exportación e Importación Masiva de Configuración

## Metadata
- **RF origen**: RF-091
- **Módulo**: 08-config-svc
- **Prioridad**: Media
- **Servicios**: config-service, tenant-service, import-export-service

---

## User Story
**Como** administrador de un tenant **quiero** exportar la configuración de mis sedes a un archivo y luego importarla para replicarla en otro tenant o restaurarla después de un incidente **para** reducir el tiempo de configuración y tener un backup recuperable.

## Objetivo
El sistema debe permitir al `tenant_admin` exportar la configuración completa (o parcial) a un archivo JSON estructurado. Este archivo incluye: horarios, tarifas, categorías, métodos de pago, impuestos, descuentos, y plantillas. También permite importar en otro tenant para replicar la configuración, con soporte para merge strategies.

## Comportamiento Específico

### Exportación
1. El admin accede a `Settings → Tools → Export / Import`.
2. Selecciona alcance:
   - `full_tenant`: toda la configuración del tenant.
   - `single_venue`: solo una sede específica.
   - `modules`: selección manual de módulos.
3. Opcionalmente marca "Incluir datos de usuario".
4. Klik en "Generate Export".
5. El sistema genera un JSON con `schema_version`, `exported_at`, `tenant_id_origin`, y todos los módulos.
6. Si incluye imágenes (logos), comprime en `.zip`.
7. El archivo se descarga en el navegador.

### Importación
1. El admin selecciona "Import Configuration" y elige el archivo `.json` o `.zip`.
2. El sistema valida: schema version, estructura de JSON, módulos presentes.
3. Muestra preview: lista de módulos, cantidad de registros, conflictos detectados.
4. El admin selecciona estrategia de merge por conflicto:
   - `skip`: no importar si ya existe.
   - `overwrite`: reemplazar con los datos del archivo.
   - `keep_both`: crear con sufijo "_imported".
5. Confirma; el sistema importa módulo por módulo.
6. Se genera `old_id -> new_id` mapping para referencias cruzadas.
7. Se registra en `import_export_logs`.
8. Se publica `CONFIG_IMPORTED`.

### Archivos no exportados
- Credenciales (API keys, secrets): se exportan como referencia, no como valores.
- Datos transaccionales: solo configuración.
- Roles predefinidos del sistema (`tenant_admin`, `operator`, `cashier`).

## Criterios de Aceptación
1. El admin puede exportar toda la configuración de su tenant a JSON.
2. La exportación incluye schema version para validación en importación.
3. Puede limitarse a una sede específica o a módulos seleccionados.
4. El admin puede importar un archivo de exportación en su tenant.
5. La importación detecta conflictos y permite elegir estrategia de merge por módulo.
6. Los IDs se reemplazan por nuevos IDs en el destino; las referencias cruzadas se actualizan.
7. Los roles predefinidos del sistema no se importan.
8. La importación genera un log detallado en `import_export_logs`.

## Datos de Entrada
- **Exportación:**
  - `scope` (string): Alcance — `full_tenant`, `single_venue`, `modules`.
  - `site_id` (UUID, opcional): ID de la sede si scope=single_venue.
  - `modules` (array[string], opcional): Lista de módulos a exportar si scope=modules.
  - `include_user_data` (boolean): Si incluye datos de usuario (opcional).
- **Importación:**
  - `file` (file): Archivo JSON o ZIP con la configuración.
  - `merge_strategy` (object): Estrategia por módulo — `skip`, `overwrite`, `keep_both`.

## Datos de Salida
- **Exportación:**
  - `export_file` (file): Archivo JSON/ZIP generado para descarga.
  - `schema_version` (string): Versión del schema para validación en importación.
  - `exported_modules` (array[string]): Lista de módulos exportados.
- **Importación:**
  - `import_preview` (object): Preview con módulos, cantidad de registros, conflictos.
  - `id_mapping` (object): Mapeo `old_id -> new_id` para referencias cruzadas.
  - `import_export_logs.id` (UUID): ID del log de importación.
  - Evento: `CONFIG_IMPORTED` publicado tras la importación.