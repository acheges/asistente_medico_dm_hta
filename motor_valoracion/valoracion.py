"""Orquestador: reúne las tres reglas deterministas en un resultado estructurado.

Función pública: valorar(entrada) -> resultado. Ver el contrato en
specs/002-captura-valoracion-dm-hta/contracts/motor-valoracion.md
"""
from . import findrisc, glucosa, tension
from .catalogos import normalizar_catalogo

ADVERTENCIA = (
    "Valoración de APOYO generada por reglas. NO sustituye el juicio del profesional de la salud."
)

# Rangos clínicos plausibles (fuera de ellos se emite una alerta de posible error de captura).
_PLAUSIBLE_SISTOLICA = (60, 300)
_PLAUSIBLE_DIASTOLICA = (30, 200)
_PLAUSIBLE_GLUCOSA = (20, 800)


def _fuera(valor, rango):
    return valor is not None and not (rango[0] <= valor <= rango[1])


def _alertas(entrada):
    alertas = []
    s = entrada.get("signos", {})
    sis, dia = s.get("ta_sistolica_mmhg"), s.get("ta_diastolica_mmhg")
    glu = entrada.get("laboratorio", {}).get("glucosa_ayuno_mgdl")
    if _fuera(sis, _PLAUSIBLE_SISTOLICA):
        alertas.append(f"Tensión sistólica fuera de rango plausible: {sis}")
    if _fuera(dia, _PLAUSIBLE_DIASTOLICA):
        alertas.append(f"Tensión diastólica fuera de rango plausible: {dia}")
    if _fuera(glu, _PLAUSIBLE_GLUCOSA):
        alertas.append(f"Glucosa fuera de rango plausible: {glu}")
    return alertas


def valorar(entrada):
    """Aplica las tres reglas y devuelve el resultado estructurado (dict).

    No inventa: si falta un dato para una regla, esa conclusión se omite y se lista en `faltantes`.
    Es determinista: la misma entrada produce siempre la misma salida.
    """
    catalogo = normalizar_catalogo(entrada.get("catalogo", "estandar"))
    paciente = entrada.get("paciente", {})
    antropometria = entrada.get("antropometria", {})
    signos = entrada.get("signos", {})
    laboratorio = entrada.get("laboratorio", {})

    conclusiones = []
    faltantes = []

    # 1) FINDRISC (reúne datos del paciente, antropometría y los reactivos)
    fr_datos = dict(entrada.get("findrisc", {}))
    fr_datos["edad"] = paciente.get("edad")
    fr_datos["sexo"] = paciente.get("sexo")
    fr_datos["imc"] = antropometria.get("imc")
    fr_datos["perimetro_cintura_cm"] = antropometria.get("perimetro_cintura_cm")
    conclusion, falta = findrisc.calcular(fr_datos)
    (faltantes.append("riesgo_diabetes_findrisc") if falta else conclusiones.append(conclusion))

    # 2) Tensión arterial
    conclusion, falta = tension.clasificar(
        signos.get("ta_sistolica_mmhg"), signos.get("ta_diastolica_mmhg"), catalogo
    )
    (faltantes.append("tension_arterial") if falta else conclusiones.append(conclusion))

    # 3) Glucosa en ayuno
    conclusion, falta = glucosa.interpretar(laboratorio.get("glucosa_ayuno_mgdl"), catalogo)
    (faltantes.append("glucosa_ayuno") if falta else conclusiones.append(conclusion))

    return {
        "catalogo": catalogo,
        "advertencia": ADVERTENCIA,
        "conclusiones": conclusiones,
        "faltantes": faltantes,
        "alertas": _alertas(entrada),
    }
