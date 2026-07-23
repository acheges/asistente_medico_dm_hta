# health_dm_hta — Captura y valoración de comorbilidad DM2 + HTA

Módulo de GNU Health (Tryton) que **extiende la evaluación** (`gnuhealth.patient.evaluation`) para
capturar, en un solo flujo, los datos de diabetes tipo 2 e hipertensión arterial, y calcular una
**valoración tentativa** con el motor determinista `motor_valoracion` (paquete propio, agnóstico de
interfaz).

## Qué agrega
- Una página **"Comorbilidad DM/HTA"** en el formulario de evaluación (dentro del notebook existente).
- Los **reactivos FINDRISC** que GNU Health no captura de fábrica (perímetro de cintura, actividad
  física, consumo de verduras/frutas, medicación antihipertensiva, antecedente de glucosa elevada,
  antecedente familiar). Reusa los campos existentes de la evaluación para tensión, IMC y glucemia.
- Un botón **"Calcular valoración"** que invoca el motor y guarda el resultado.
- Campos de resultado: categoría FINDRISC, clasificación de tensión, interpretación de glucosa, y el
  **resultado estructurado (JSON)** consumible por el modelo de lenguaje (Feature C).

## Depende de
- Módulo GNU Health `health`.
- Paquete Python `motor_valoracion` (instalado en el mismo entorno; ver `pyproject.toml` en la raíz).

## Configuración
- **Catálogo de umbrales**: por evaluación (campo *Catálogo*) o por defecto vía la variable de
  entorno `DMHTA_CATALOGO` (`estandar` | `nom`). Sin configuración, se usa `estandar`.

## La IA no sustituye al médico
La valoración es **de apoyo, tentativa y editable**; el formulario muestra la advertencia explícita
(Constitución art. III y IV). El cálculo es **determinista y auditable**; el modelo de lenguaje
(Feature C) solo interpretará/comunicará este resultado, no lo recalcula.

## Prueba de integración
Ver `tests/integracion_dmhta.py` (se ejecuta dentro del contenedor con proteus).
