# Asistente Médico DM/HTA

Asistente de **apoyo clínico** para la comorbilidad **Diabetes Mellitus tipo 2 (DM) + Hipertensión
Arterial (HTA)** en atención primaria, construido **sobre GNU Health** (sistema de expediente clínico
electrónico libre).

La valoración de riesgo la calcula un **motor de reglas deterministas** (FINDRISC, clasificación de
tensión, interpretación de glucosa); un **modelo de lenguaje** la traduce a lenguaje clínico claro.
La IA **interpreta y comunica, no diagnostica**. La identidad del paciente **nunca sale** del núcleo:
una *aduana* de seudonimización la retira antes de cualquier consulta al modelo.

## Cómo levantarlo

Requiere **Docker** y **docker compose**.

```bash
cd infra
cp .env.example .env        # ajusta credenciales; para IA, la llave del proveedor
docker compose up -d
```

- Interfaz web: **http://localhost:8000** (usuario `admin`; contraseña en `infra/.env`).
- Asistente de IA (opcional): pon `COMPOSE_PROFILES=ia` y tu `AI_API_KEY` en `infra/.env`.

## Mapa del código

| Carpeta | Qué contiene |
|---|---|
| `motor_valoracion/` | Motor determinista (FINDRISC, tensión, glucosa). Paquete Python sin dependencias de interfaz. |
| `ai_service/` | Servicio intérprete (FastAPI): cliente de modelo agnóstico + prompt. |
| `gnuhealth_modules/health_dm_hta/` | Captura de la comorbilidad + cálculo de la valoración. |
| `gnuhealth_modules/health_dm_hta_ia/` | Aduana de seudonimización + interpretación con IA. |
| `gnuhealth_modules/health_dm_hta_ui/` | Pantalla clínica propia (menú, lista, formulario). |
| `infra/` | `docker-compose.yml`, Dockerfiles, `custom.css`, fuentes, `.env.example`. |

## Estado

Entre **prueba de concepto (POC)** y **producto mínimo viable (PMV)**.
