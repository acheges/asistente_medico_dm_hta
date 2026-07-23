"""Interpretación de la glucosa en ayuno (mg/dL) según el catálogo activo."""
from .catalogos import glucosa_cortes, normalizar_catalogo


def interpretar(glucosa_mgdl, catalogo="estandar"):
    """Devuelve (conclusion, faltante). Si falta el valor, (None, True)."""
    if glucosa_mgdl is None:
        return None, True

    cat = normalizar_catalogo(catalogo)
    normal_max, diabetes_min = glucosa_cortes(cat)
    g = glucosa_mgdl

    if g >= diabetes_min:
        etiqueta, regla = "Rango de diabetes", f"{cat}: >= {diabetes_min}"
    elif g >= normal_max:
        etiqueta, regla = "Glucosa alterada", f"{cat}: {normal_max}-{diabetes_min - 1}"
    else:
        etiqueta, regla = "Normal", f"{cat}: < {normal_max}"

    return {
        "dominio": "glucosa_ayuno",
        "etiqueta": etiqueta,
        "valor": {"glucosa_mgdl": g},
        "entradas": {"glucosa_mgdl": g},
        "regla_aplicada": regla,
        "editado_por_humano": False,
    }, False
