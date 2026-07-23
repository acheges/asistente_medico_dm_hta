# health_dm_hta_ui — Pantalla clínica DM/HTA (Feature D)

Módulo de **presentación y recorrido**. No define modelos ni campos nuevos: da al médico una pantalla
propia, limpia y bien organizada sobre el modelo existente `gnuhealth.patient.evaluation`, para que
el trabajo de las Features B (motor determinista) y C (asistente de lenguaje) sea **fácil de alcanzar
y evidente**.

## Qué aporta

- **Dos puertas de entrada** a las valoraciones DM/HTA:
  - **Menú** "Salud → DM/HTA": lista todas las valoraciones DM/HTA (filtrables por paciente).
  - **Acción relacionada** desde el paciente (ícono 🔗 → "Valoraciones DM/HTA"): solo las de ese
    paciente. Al crear una nueva desde aquí, el paciente viene preseleccionado.
- **Lista propia (panel longitudinal)**: 7 columnas legibles (paciente, fecha, puntaje y categoría
  FINDRISC, tensión arterial, glucosa, fecha de interpretación IA), ordenadas por fecha descendente
  (lo más reciente arriba), como una sección de laboratorio.
- **Formulario propio y limpio** (vista independiente, NO hereda el formulario nativo gigante), en una
  sola pantalla, con **cuatro grupos rotulados por procedencia**:
  1. **Datos capturados por el profesional** — editables + botón "Calcular valoración".
  2. **Calculado por reglas deterministas** — resultados reproducibles (según el catálogo elegido:
     estándar internacional o Normas mexicanas).
  3. **Redactado por el modelo de lenguaje** — texto de apoyo editable, con la advertencia
     "material de APOYO, NO sustituye al profesional", el modelo y la fecha; botón "Interpretar con IA".
  4. **Detalle técnico** (pestaña) — la valoración estructurada (JSON), secundaria, fuera del camino.

## Cómo identifica una "valoración DM/HTA"

La lista filtra por la marca **`dmhta_es_valoracion`**, un campo booleano que vive en el módulo base
`health_dm_hta` (es metadato, no presentación) y que se **enciende al calcular** la valoración. Así la
lista muestra solo valoraciones DM/HTA, sin mezclar consultas ajenas.

## Dependencias

`health_dm_hta_ia` → `health_dm_hta` → `health`. Reutiliza el motor (`motor_valoracion`) y el
`ai-service` existentes; no los modifica.

## Instalación

Se copia a la imagen en `infra/gnuhealth/Dockerfile` y el `entrypoint.sh` lo activa solo (activa todo
módulo presente). No requiere pasos manuales.

## Fuera de alcance (deuda anotada)

Las listas **nativas** de GNU Health con columnas amontonadas (p. ej. "Condiciones") NO se arreglan
aquí. Solución identificada para cuando se retome: heredar la vista nativa y marcar columnas con el
atributo `optional` de Tryton, y revisar el defecto de CSS (`overflow: hidden`) del cliente Sao.
