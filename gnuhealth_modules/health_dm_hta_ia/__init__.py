"""Módulo health_dm_hta_ia: la ADUANA de la Feature C.

Vive en la zona de confianza (dentro de GNU Health). Construye el payload seudonimizado, lo envía al
ai-service (ciego a la identidad), registra el egreso en una bitácora y re-liga el texto a la
evaluación. La seudonimización la hace la aduana (código determinista), nunca el modelo.
"""
from trytond.pool import Pool

from . import health_dm_hta_ia


def register():
    Pool.register(
        health_dm_hta_ia.PatientEvaluation,
        health_dm_hta_ia.IaEgreso,
        module="health_dm_hta_ia",
        type_="model",
    )
