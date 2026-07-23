"""Puntaje FINDRISC (Finnish Diabetes Risk Score) y categoría de riesgo de diabetes tipo 2.

El puntaje y las categorías son los del instrumento validado (0-26 puntos).
"""
from .catalogos import findrisc_categoria

_FAMILIAR = {"no": 0, "segundo_grado": 3, "primer_grado": 5}


def _pts_edad(edad):
    if edad is None:
        return None
    if edad < 45:
        return 0
    if edad <= 54:
        return 2
    if edad <= 64:
        return 3
    return 4


def _pts_imc(imc):
    if imc is None:
        return None
    if imc < 25:
        return 0
    if imc <= 30:
        return 1
    return 3


def _pts_cintura(cm, sexo):
    if cm is None or sexo is None:
        return None
    # Umbral masculino para 'm'; para el resto se usa el umbral femenino.
    if str(sexo).lower() == "m":
        if cm < 94:
            return 0
        return 3 if cm <= 102 else 4
    if cm < 80:
        return 0
    return 3 if cm <= 88 else 4


def calcular(datos):
    """Calcula la conclusión FINDRISC.

    `datos`: dict con edad, sexo, imc, perimetro_cintura_cm, actividad_fisica_diaria,
    consumo_verduras_frutas_diario, medicacion_antihipertensiva, antecedente_glucosa_elevada,
    antecedente_familiar_diabetes.

    Devuelve (conclusion, faltante): si falta cualquier dato para puntuar, (None, True).
    """
    af = datos.get("actividad_fisica_diaria")
    vf = datos.get("consumo_verduras_frutas_diario")
    ma = datos.get("medicacion_antihipertensiva")
    ag = datos.get("antecedente_glucosa_elevada")
    fam = datos.get("antecedente_familiar_diabetes")

    entradas = {
        "edad": _pts_edad(datos.get("edad")),
        "imc": _pts_imc(datos.get("imc")),
        "cintura": _pts_cintura(datos.get("perimetro_cintura_cm"), datos.get("sexo")),
        "actividad_fisica": None if af is None else (0 if af else 2),
        "verduras_frutas": None if vf is None else (0 if vf else 1),
        "medicacion_antihipertensiva": None if ma is None else (2 if ma else 0),
        "antecedente_glucosa": None if ag is None else (5 if ag else 0),
        "antecedente_familiar": _FAMILIAR.get(fam) if fam is not None else None,
    }

    if any(v is None for v in entradas.values()):
        return None, True

    puntaje = sum(entradas.values())
    _, etiqueta, regla = findrisc_categoria(puntaje)
    return {
        "dominio": "riesgo_diabetes_findrisc",
        "etiqueta": etiqueta,
        "valor": {"puntaje": puntaje},
        "entradas": entradas,
        "regla_aplicada": regla,
        "editado_por_humano": False,
    }, False
