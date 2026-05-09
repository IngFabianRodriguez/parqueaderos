# SPEC-02-009 — Almacenar imágenes de captura con hash para auditoría

## Metadata
- **RF origen**: RF-009
- **Módulo**: 02-anpr
- **Prioridad**: Media
- **Servicios**: anpr-service, storage-service

---

## User Story
**Como** Sistema (almacenamiento automático) **quiero** almacenar la imagen de cada captura de placa con su hash SHA-256 para auditoría **para** garantizar la integridad de las imágenes como evidencia en disputas de cobro, recursos de tránsito o investigaciones.

## Objetivo
Cada imagen capturada por el sistema ANPR en entrada o salida debe almacenarse de forma segura con: (1) la imagen original en object storage (S3 o compatible), (2) un hash SHA-256 calculado sobre la imagen original, (3) metadatos (timestamp, sede, placa, confianza). El hash permite verificar que la imagen no ha sido alterada. Las imágenes se retienen mínimo 90 días.

## Comportamiento Específico

### Happy Path
1. ANPR-service captura imagen de placa en entrada o salida
2. ANPR-service calcula SHA-256 hash de la imagen cruda
3. ANPR-service envía imagen + hash + metadatos a storage-service
4. Storage-service sube imagen a object storage (S3/MinIO/Cloudflare R2)
5. Storage-service retorna URL de la imagen almacenada
6. ANPR-service actualiza el registro de entrada/salida con imagen_url y hash_sha256
7. Sistema programa tarea de limpieza para eliminar imágenes > 90 días

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Imagen corrupta o ilegible | Se almacena igualmente con hash del archivo recibido y se marca como 'low_quality' |
| Object storage no disponible | Se guarda en base de datos como BLOB temporal y se programa retry cada 5 minutos |
| Hash no coincide al verificar (imagen alterada) | Se genera alerta de seguridad y se marca el registro como 'sospechoso' |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| imagen | BINARY | Imagen en formato JPEG/PNG | Sí |
| registro_id | UUID | ID del registro de entrada/salida asociado | Sí |
| tipo_captura | VARCHAR | 'entrada' o 'salida' | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| imagen_url | VARCHAR | — |
| hash_sha256 | VARCHAR | — |
| tamano_bytes | INTEGER | — |
| timestamp_almacenamiento | TIMESTAMP | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Cada imagen tiene un hash único y reproducible
2. La verificación de hash debe poder hacerse sin acceso al object storage (solo con hash y archivo)
3. Almacenamiento mínimo 90 días configurable por tenant

## Endpoints
- `POST /api/v1/storage/imagenes` — Almacena imagen de captura

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Hash SHA-256 se calcula sobre el archivo raw antes de cualquier compresión
- La ruta de almacenamiento en S3: `{tenant_id}/{sede_id}/{YYYY-MM}/{registro_id}.jpg`
- El metadata de la imagen en S3 incluye: placa, confianza_ocr, timestamp_captura, tipo_captura
- La verificación de integridad se hace con: `sha256(imagen_descargada) == hash_sha256_almacenado`
- El TTL de 90 días es configurable por tenant en la tabla configuracion_tenant
- Si el registro se elimina, la imagen también debe eliminarse (cascade delete en storage)