"""Módulo health_dm_hta: captura de comorbilidad DM2 + HTA y valoración determinista.

Extiende la evaluación de GNU Health (gnuhealth.patient.evaluation) con los reactivos FINDRISC
faltantes y los campos de la valoración, e invoca el paquete `motor_valoracion` (motor determinista,
agnóstico de interfaz) para calcular la valoración tentativa.
"""
from trytond.pool import Pool

from . import health_dm_hta


def register():
    Pool.register(
        health_dm_hta.PatientEvaluation,
        module="health_dm_hta",
        type_="model",
    )
