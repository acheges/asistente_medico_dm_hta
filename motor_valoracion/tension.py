"""Clasificación de la tensión arterial según el catálogo de umbrales activo."""
from .catalogos import cortes_tension, normalizar_catalogo


def clasificar(sistolica, diastolica, catalogo="estandar"):
    """Devuelve (conclusion, faltante). Si falta un valor, (None, True)."""
    if sistolica is None or diastolica is None:
        return None, True

    cat = normalizar_catalogo(catalogo)
    c = cortes_tension(cat)
    s, d = sistolica, diastolica

    cs, cd = c["crisis"]
    e2s, e2d = c["etapa2"]
    e1s, e1d = c["etapa1"]
    els, _ = c["elevada"]
    eld = c["elevada"][1]

    if s > cs or d > cd:
        clave, etiqueta = "crisis", "Crisis hipertensiva"
    elif s >= e2s or d >= e2d:
        clave, etiqueta = "etapa2", "Hipertensión etapa 2"
    elif s >= e1s or d >= e1d:
        clave, etiqueta = "etapa1", "Hipertensión etapa 1"
    elif s >= els or (eld is not None and d >= eld):
        clave, etiqueta = "elevada", "Normal alta" if cat == "nom" else "Elevada"
    else:
        clave, etiqueta = "normal", "Normal"

    return {
        "dominio": "tension_arterial",
        "etiqueta": etiqueta,
        "valor": {"sistolica": s, "diastolica": d},
        "entradas": {"sistolica": s, "diastolica": d},
        "regla_aplicada": f"{cat}: categoría '{clave}'",
        "editado_por_humano": False,
    }, False
