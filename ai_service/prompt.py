"""Arma el prompt de intérprete/comunicador.

Fija el rol por diseño: el modelo COMUNICA/EXPLICA una valoración ya calculada; no diagnostica ni
recalcula. Recibe el payload seudonimizado (sin datos de identificación personal).
"""
import json

SYSTEM = (
    "Eres un asistente que COMUNICA en español, de forma clara y empática, una valoración clínica "
    "YA CALCULADA por reglas deterministas. Tu tarea es INTERPRETAR y EXPLICAR ese resultado para el "
    "personal de salud de atención primaria. NO diagnostiques, NO recalcules, NO inventes datos y NO "
    "tomes decisiones clínicas. Recuerda de forma explícita que es material de APOYO y que NO "
    "sustituye el juicio del profesional de la salud."
)


def construir(payload):
    """Devuelve (system_prompt, user_prompt) a partir del payload seudonimizado."""
    user = (
        "Valoración estructurada del paciente (sin datos que lo identifiquen):\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nExplica en lenguaje claro, para el profesional de salud, el riesgo y las conclusiones, "
        "y recuérdale que es apoyo y no sustituye su juicio."
    )
    return SYSTEM, user
