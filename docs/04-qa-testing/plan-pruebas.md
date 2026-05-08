# Estrategia de Testing

## Filosofía

- **Shift-left**: Integrar pruebas lo más temprano posible en el ciclo de desarrollo
- **Automatización máxima**: Minimizar pruebas manuales, priorizar pipelines automatizados
- **Tests en todas las capas**: Desde unitarios hasta E2E, cubriendo cada nivel de la arquitectura

## Pirámide de Tests

```
        /\
       /E2E\         ← Pocos, costosos, validación de flujos completos
      /------\
     /Integración\  ← APIs, bases de datos, servicios externos
    /------------\
   /  Unitarios    \ ← Base de la pirámide, más numerosos y rápidos
  /________________\
```

- **Unitarios** (base, más numerosos)
- **Integración** (APIs, BD)
- **E2E** (flujos completos de usuario)

## Cobertura Objetivo

- **80%** de código cubierto por tests unitarios
- Métrica medida con coverage.py (Python) y Jest coverage (TypeScript)

## Frameworks

| Tipo | Framework | Lenguaje |
|------|-----------|----------|
| Unitarios | pytest | Python |
| Unitarios | Jest | TypeScript |
| E2E | Playwright | TypeScript/JavaScript |

## Test Unitarios

### Qué probar

- Lógica de tarifas (cálculo de costos por minuto, franjas horarias)
- Cálculo de duración (tiempo entre entrada y salida)
- ANPR parsing (extracción de placas desde imágenes)
- Auth JWT (generación, validación, expiración de tokens)

### Qué NO probar

- Frameworks (Django, FastAPI, Express)
- Librerías externas (boto3, psycopg2, paho-mqtt)
- Código generado automáticamente

## Test de Integración

### APIs contra PostgreSQL real

- Usar **Docker Compose** con imagen oficial de PostgreSQL
- Ejecutar migraciones antes de cada suite
- Limpiar datos de prueba después de cada test

### MQTT pub/sub

- Usar **Mosquitito** en contenedor Docker
- Verificar publicación y suscripción de mensajes
- Simular escenarios de desconexión y reconexión

## Test E2E

### Flujos críticos

1. **Entrada-ANPR-registro**: Vehículo entra → cámara lee placa → sistema registra entrada
2. **Pago-confirmación-apertura talanquera**: Usuario paga → pasarela confirma → talanquera abre
3. **Flujo completo entrada-pago-salida**: Recorrido end-to-end del usuario

## CI/CD

### Pipeline en GitHub Actions

```
lint → type-check → test → build → deploy to staging
```

1. **lint**: ESLint, flake8, ruff
2. **type-check**: mypy, TypeScript compiler
3. **test**: pytest + Jest + Playwright
4. **build**: Docker images
5. **deploy**: Despliegue a entorno staging

## Entornos

| Entorno | Descripción |
|---------|-------------|
| dev | Desarrollo local con Docker Compose |
| staging | Cloud, réplica de producción |
| prod | Producción con alta disponibilidad |

## Criterios de Calidad Gate

- **Coverage >= 80%** en tests unitarios
- **Todos los tests passing** en pipeline CI
- **Ningún blocker o critical** en SonarQube
- Tiempo de ejecución de tests E2E < 10 minutos
