"""Prueba de privacidad de la aduana: el payload NO contiene datos de identificación personal,
y el validador "prohibido PII" FALLA CERRADA. Carga aduana.py directo (sin el __init__ que
importa trytond), así corre también en el host.
"""
import importlib.util
import os

_HERE = os.path.dirname(__file__)
_spec = importlib.util.spec_from_file_location("aduana", os.path.join(_HERE, "..", "aduana.py"))
aduana = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(aduana)


_DATOS = {
    "edad": 58,
    "sexo": "f",
    "valoracion": {
        "catalogo": "estandar",
        "conclusiones": [
            {"dominio": "tension_arterial", "etiqueta": "Hipertensión etapa 1",
             "entradas": {"sistolica": 138, "diastolica": 88}, "regla_aplicada": "…"},
        ],
    },
}


def test_payload_no_contiene_pii():
    payload, campos = aduana.construir_payload(_DATOS)
    texto = str(payload).lower()
    for prohibido in ("nombre", "curp", "direccion", "juan", "party"):
        assert prohibido not in texto
    assert payload["paciente"] == {"edad": 58, "sexo": "f"}
    assert "valoracion" in campos


def test_token_es_efimero_y_unico():
    p1, _ = aduana.construir_payload(_DATOS)
    p2, _ = aduana.construir_payload(_DATOS)
    assert p1["token"] != p2["token"]
    assert p1["token"].startswith("req-")


def test_validador_falla_cerrada_ante_pii():
    # Si la valoración trajera un campo prohibido (p. ej. 'curp'), el egreso se bloquea.
    datos = {"edad": 58, "sexo": "f", "valoracion": {"curp": "XXXX010101HDF"}}
    try:
        aduana.construir_payload(datos)
        assert False, "debió bloquear el egreso"
    except ValueError as e:
        assert "prohibido" in str(e).lower()
