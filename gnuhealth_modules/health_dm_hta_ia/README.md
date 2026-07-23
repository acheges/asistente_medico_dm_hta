# health_dm_hta_ia — La aduana (Feature C)

Módulo de GNU Health que vive en la **zona de confianza** (dentro del core). Es la **aduana**: a partir
de una evaluación con valoración (Feature B), construye un **payload seudonimizado**, lo envía al
`ai-service` (ciego a la identidad), guarda el texto de apoyo y registra el egreso en una bitácora.

## Qué agrega
- Página **"Interpretación IA"** en la evaluación, con el botón **"Interpretar con IA"** y el texto de
  apoyo (con advertencia de que no sustituye al profesional, editable).
- Campos: `dmhta_ia_texto`, `dmhta_ia_texto_editado`, `dmhta_ia_modelo`, `dmhta_ia_fecha`.
- Modelo de **bitácora** `gnuhealth.dm_hta.ia_egreso` (token, campos enviados, fecha, modelo,
  resultado) — **sin identidad**.

## La aduana (`aduana.py`)
- Construye el payload como un **pipeline** de pasos (hoy: valoración + edad/sexo). Es **extensible y
  versionado**: mañana se suman síntomas/historial sin rediseño.
- Un **token efímero** por solicitud (se descarta tras re-ligar la respuesta).
- Un **validador "prohibido PII" que FALLA CERRADA**: si detectara un dato de identificación personal
  en el payload, **bloquea** el egreso.

## Garantías de privacidad
- La seudonimización la hace la aduana (código determinista), **nunca** el modelo.
- La PII **nunca** cruza al `ai-service` ni al proveedor.
- El mapa token↔identidad es **efímero** y vive solo en el core; nunca sale ni se registra.
- Solo se registran en bitácora los **egresos exitosos** (un fallo de conexión no egresa nada).

## Configuración
- `AI_SERVICE_URL` (URL del ai-service en la red interna), `AI_TIMEOUT`, `AI_DESID_TOTAL`
  (des-identificación total). El proveedor/modelo se configuran en el `ai-service`.

## Pruebas
`tests/test_aduana.py` — el payload no contiene PII, el token es efímero/único, y el validador falla
cerrada ante PII inyectada.
