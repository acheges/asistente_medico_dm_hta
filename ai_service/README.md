# ai-service — asistente de lenguaje intérprete

Servicio HTTP mínimo, **sin estado** y **ciego a la identidad**. Recibe un payload YA seudonimizado
(sin datos de identificación personal) y devuelve un texto de apoyo generado por un modelo de lenguaje.
No guarda nada, no ve identidad, no hace redacción.

## Rol
El modelo **interpreta y comunica** una valoración ya calculada por reglas deterministas (Feature B).
NO diagnostica ni recalcula. El texto es **apoyo** y **no sustituye** al profesional.

## API
- `GET /salud` → `{"estado":"ok"}` (healthcheck).
- `POST /interpretar` → recibe el [payload de egreso](../specs/003-asistente-llm-interprete/contracts/payload-egreso.md), devuelve `{"texto": "...", "modelo": "..."}`.

## Cliente agnóstico
Soporta dos estilos de API por configuración (`AI_PROVIDER_STYLE`):
- `openai` → `POST {AI_BASE_URL}/chat/completions` (el que usa **Kimi K2.6 vía opencode Zen**).
- `anthropic` → `POST {AI_BASE_URL}/messages`.

Cambiar proveedor/modelo = cambiar variables de entorno, sin tocar código.

## Configuración (variables de entorno, NUNCA versionadas)
`AI_PROVIDER_STYLE`, `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT`, `AI_DRY_RUN`.
Con `AI_DRY_RUN=true` responde un texto simulado sin llamar al proveedor (pruebas sin costo).

## Despliegue
Contenedor **opcional** (perfil `ia` de Docker Compose). Ver `infra/docker-compose.yml` y
`specs/003-asistente-llm-interprete/quickstart.md`.

## Pruebas
`ai_service/tests/` — arman la petición para estilo OpenAI y Anthropic y prueban el modo simulado
(sin red).
