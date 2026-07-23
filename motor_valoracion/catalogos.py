"""Catálogos de umbrales, seleccionables por configuración.

Dos catálogos: `estandar` (internacional, por defecto) y `nom` (normas mexicanas). El puntaje y
las categorías FINDRISC son iguales en ambos (instrumento validado); lo que cambia entre catálogos
son los cortes de tensión arterial y de glucosa.

Los cortes de NOM son de referencia (NOM-015-SSA2, NOM-030-SSA2) y deben validarse clínicamente.
"""

CATALOGOS_VALIDOS = ("estandar", "nom")


def normalizar_catalogo(nombre):
    """Devuelve un nombre de catálogo válido; si no lo es, cae a 'estandar'."""
    return nombre if nombre in CATALOGOS_VALIDOS else "estandar"


# --- FINDRISC: categorías por puntaje (igual en ambos catálogos) ---
def findrisc_categoria(puntaje):
    """Devuelve (clave, etiqueta, regla_aplicada) para un puntaje FINDRISC (0-26)."""
    if puntaje < 7:
        return ("bajo", "Riesgo bajo", "FINDRISC: <7 = bajo")
    if puntaje <= 11:
        return ("ligeramente_elevado", "Riesgo ligeramente elevado", "FINDRISC: 7-11 = ligeramente elevado")
    if puntaje <= 14:
        return ("moderado", "Riesgo moderado", "FINDRISC: 12-14 = moderado")
    if puntaje <= 20:
        return ("alto", "Riesgo alto", "FINDRISC: 15-20 = alto")
    return ("muy_alto", "Riesgo muy alto", "FINDRISC: >20 = muy alto")


# --- Glucosa en ayuno (mg/dL): (corte_normal, corte_diabetes) ---
# normal < corte_normal ; alterada [corte_normal, corte_diabetes) ; diabetes >= corte_diabetes
_GLUCOSA = {
    "estandar": (100, 126),  # normal <100 · alterada 100-125 · diabetes >=126
    "nom": (100, 126),       # NOM-015-SSA2 coincide en glucosa de ayuno
}


def glucosa_cortes(catalogo):
    return _GLUCOSA[normalizar_catalogo(catalogo)]


# --- Tensión arterial (mmHg): cortes por catálogo ---
# Cada catálogo define su escalera de clasificación. Ver tension.py para el algoritmo.
CORTES_TENSION = {
    "estandar": {  # referencia internacional (estilo ACC/AHA)
        "crisis": (180, 120),
        "etapa2": (140, 90),
        "etapa1": (130, 80),
        "elevada": (120, None),
    },
    "nom": {  # referencia NOM-030-SSA2 (validar clínicamente)
        "crisis": (180, 120),
        "etapa2": (160, 100),
        "etapa1": (140, 90),
        "elevada": (130, 85),
    },
}


def cortes_tension(catalogo):
    return CORTES_TENSION[normalizar_catalogo(catalogo)]
