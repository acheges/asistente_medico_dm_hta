# Despliegue de GNU Health (infra/)

Levanta GNU Health (backend trytond + API JSON-RPC + cliente web Sao) y PostgreSQL con un
solo comando. Toda la configuración vive en `infra/.env` (no se versiona).

## Puesta en marcha (rápida)

```bash
# 1. Crear tu configuración a partir de la plantilla y ajustar contraseñas/idioma.
cp infra/.env.example infra/.env
#    Editar infra/.env: POSTGRES_PASSWORD, ADMIN_PASSWORD, GNUHEALTH_PORT, GNUHEALTH_LANG...

# 2. Levantar todo.
docker compose -f infra/docker-compose.yml up -d --build
```

Abre `http://localhost:8000` (o el `GNUHEALTH_PORT` que hayas puesto).
Entra con: **base** `gnuhealth`, **usuario** `admin`, **contraseña** = tu `ADMIN_PASSWORD`.

> La primera vez tarda unos minutos: construye la imagen, instala módulos y activa la base.

## Configuración (infra/.env)

| Variable | Para qué | Por defecto |
|----------|----------|-------------|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciales de PostgreSQL | `gnuhealth` |
| `DB_HOST` / `DB_PORT` | Dónde está la base (dentro de la red de compose) | `db` / `5432` |
| `GNUHEALTH_PORT` | Puerto del navegador/API | `8000` |
| `GNUHEALTH_LANG` | Idioma de la interfaz (`es` o `es_419`) | `es_419` |
| `ADMIN_PASSWORD` | Contraseña del usuario `admin` | (cambiar fuera de local) |
| `LOAD_DEMO_DATA` | Cargar pacientes ficticios de demostración | `false` |
| `COMPOSE_PROFILES` | Encender servicios opcionales (`fhir`, `thalamus`) | vacío |
| `FHIR_PORT` / `THALAMUS_PORT` | Puertos de los servicios opcionales | `8080` / `8443` |

## Servicios opcionales

Apagados por defecto. Para encenderlos, lista su perfil en `infra/.env`:

```bash
COMPOSE_PROFILES=fhir            # solo FHIR
COMPOSE_PROFILES=fhir,thalamus   # ambos
```

Ambos son **experimentales** (ver [research.md](../specs/001-despliegue-gnu-health/research.md) y
[docs/despliegue-vps.md](../docs/despliegue-vps.md)). La vía principal de datos es la API
**JSON-RPC de trytond**, no FHIR.

## Apagado

```bash
docker compose -f infra/docker-compose.yml down       # conserva los datos (volúmenes)
docker compose -f infra/docker-compose.yml down -v    # BORRA los datos
```

## Más

- Guía de validación paso a paso: [../specs/001-despliegue-gnu-health/quickstart.md](../specs/001-despliegue-gnu-health/quickstart.md)
- Despliegue en un VPS: [../docs/despliegue-vps.md](../docs/despliegue-vps.md)
- Backend (modelos y endpoints para Features B y C): [../docs/backend-gnuhealth.md](../docs/backend-gnuhealth.md)
