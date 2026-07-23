"""Pruebas del motor de valoración: un caso representativo por categoría, más faltantes,
fuera de rango, reproducibilidad y cambio de catálogo (US1 y US2).

Se ejercita el CÁLCULO real (no solo que 'no truene'), aplicando la lección de la Feature A.
"""
from motor_valoracion import valorar
from motor_valoracion import findrisc, glucosa, tension


def _conclusion(resultado, dominio):
    for c in resultado["conclusiones"]:
        if c["dominio"] == dominio:
            return c
    return None


# --- FINDRISC: un caso por categoría ---
def _fr(edad, sexo, imc, cintura, af, vf, med, antglu, fam):
    d = {
        "edad": edad, "sexo": sexo, "imc": imc, "perimetro_cintura_cm": cintura,
        "actividad_fisica_diaria": af, "consumo_verduras_frutas_diario": vf,
        "medicacion_antihipertensiva": med, "antecedente_glucosa_elevada": antglu,
        "antecedente_familiar_diabetes": fam,
    }
    return findrisc.calcular(d)[0]


def test_findrisc_bajo():
    c = _fr(30, "f", 22.0, 70, True, True, False, False, "no")
    assert c["valor"]["puntaje"] == 0
    assert c["etiqueta"] == "Riesgo bajo"


def test_findrisc_moderado():
    c = _fr(50, "f", 27.0, 85, False, False, False, False, "segundo_grado")
    assert c["valor"]["puntaje"] == 12
    assert c["etiqueta"] == "Riesgo moderado"


def test_findrisc_alto():
    c = _fr(58, "f", 32.0, 95, False, False, True, False, "primer_grado")
    assert c["valor"]["puntaje"] == 20
    assert c["etiqueta"] == "Riesgo alto"


def test_findrisc_muy_alto():
    c = _fr(65, "m", 32.0, 105, False, False, True, True, "primer_grado")
    assert c["valor"]["puntaje"] == 26
    assert c["etiqueta"] == "Riesgo muy alto"


# --- Tensión arterial (catálogo estándar): un caso por categoría ---
def test_tension_normal():
    assert tension.clasificar(115, 75)[0]["etiqueta"] == "Normal"


def test_tension_etapa1():
    assert tension.clasificar(135, 85)[0]["etiqueta"] == "Hipertensión etapa 1"


def test_tension_etapa2():
    assert tension.clasificar(150, 95)[0]["etiqueta"] == "Hipertensión etapa 2"


def test_tension_crisis():
    assert tension.clasificar(190, 125)[0]["etiqueta"] == "Crisis hipertensiva"


# --- Glucosa en ayuno: un caso por categoría ---
def test_glucosa_normal():
    assert glucosa.interpretar(90.0)[0]["etiqueta"] == "Normal"


def test_glucosa_alterada():
    assert glucosa.interpretar(118.0)[0]["etiqueta"] == "Glucosa alterada"


def test_glucosa_diabetes():
    assert glucosa.interpretar(140.0)[0]["etiqueta"] == "Rango de diabetes"


# --- Valoración completa: estructura y advertencia ---
def _entrada_completa(catalogo="estandar"):
    return {
        "paciente": {"edad": 58, "sexo": "f"},
        "antropometria": {"imc": 32.0, "perimetro_cintura_cm": 95.0},
        "signos": {"ta_sistolica_mmhg": 135, "ta_diastolica_mmhg": 85},
        "laboratorio": {"glucosa_ayuno_mgdl": 118.0},
        "findrisc": {
            "actividad_fisica_diaria": False, "consumo_verduras_frutas_diario": False,
            "medicacion_antihipertensiva": True, "antecedente_glucosa_elevada": False,
            "antecedente_familiar_diabetes": "primer_grado",
        },
        "catalogo": catalogo,
    }


def test_valoracion_completa_tres_conclusiones_y_advertencia():
    r = valorar(_entrada_completa())
    assert len(r["conclusiones"]) == 3
    assert r["faltantes"] == []
    assert "NO sustituye" in r["advertencia"]
    # cada conclusión trae etiqueta + entradas + regla (auditable, US3)
    for c in r["conclusiones"]:
        assert c["etiqueta"] and c["entradas"] and c["regla_aplicada"]


def test_faltantes_no_inventa():
    entrada = _entrada_completa()
    entrada["laboratorio"] = {}  # sin glucosa
    r = valorar(entrada)
    assert "glucosa_ayuno" in r["faltantes"]
    assert _conclusion(r, "glucosa_ayuno") is None


def test_alerta_fuera_de_rango():
    entrada = _entrada_completa()
    entrada["signos"]["ta_sistolica_mmhg"] = 400  # implausible
    r = valorar(entrada)
    assert any("sistólica" in a for a in r["alertas"])


def test_reproducible():
    assert valorar(_entrada_completa()) == valorar(_entrada_completa())


# --- US2: cambiar de catálogo cambia la categoría ---
def test_catalogo_cambia_categoria_tension():
    est = _conclusion(valorar(_entrada_completa("estandar")), "tension_arterial")
    nom = _conclusion(valorar(_entrada_completa("nom")), "tension_arterial")
    # 135/85: estándar = etapa 1 ; NOM = normal alta (elevada)
    assert est["etiqueta"] == "Hipertensión etapa 1"
    assert nom["etiqueta"] == "Normal alta"
    assert est["etiqueta"] != nom["etiqueta"]
