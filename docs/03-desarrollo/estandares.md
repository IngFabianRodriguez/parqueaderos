# Estándares de Código y Convenciones

## Convenciones de Nomenclatura

### Python

- Funciones y variables: `snake_case`
- Clases: `PascalCase`
- Constantes: `SCREAMING_SNAKE`

### TypeScript / JavaScript

- Variables y funciones: `camelCase`
- Componentes: `PascalCase`

## Formateo de Código

- **Python**: Ruff (configuración en `pyproject.toml`)
- **TypeScript**: Prettier

## Linting

- **Python**: pyright (modo strict)
- **TypeScript**: ESLint

## Commits

Se utiliza el formato **Conventional Commits**:

- `feat:` — Nueva funcionalidad
- `fix:` — Corrección de errores
- `docs:` — Documentación
- `refactor:` — Refactorización
- `test:` — Pruebas
- `chore:` — Mantenimiento

## Ramas

- `main` — Producción
- `develop` — Integración
- `feature/*` — Nuevas funcionalidades
- `fix/*` — Correcciones
- `docs/*` — Documentación

## Pull Requests

- Mínimo 1 revisión antes de merge
- CI pasando
- Tests pasando

## Documentación de Código

- **Python**: Docstrings en español siguiendo Google Style
- **TypeScript**: JSDoc

## Mensajes de Commit de Ejemplo

```
feat(anpr): add plate recognition via external API
fix(payments): handle timeout on Wompi callback
docs(readme): update deployment instructions
```
