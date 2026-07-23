#!/usr/bin/env python3
"""Carga OPCIONAL de datos de demostración en GNU Health.

Se ejecuta solo cuando LOAD_DEMO_DATA=true (lo decide el entrypoint.sh).
Usa proteus (la librería de scripting oficial de Tryton) contra la MISMA base
de datos, sin necesidad de un servidor HTTP corriendo.

Crea:
  1. Una institución de salud de atención primaria (necesaria para el flujo clínico).
  2. Unos pacientes ficticios.

Es IDEMPOTENTE: si algo ya existe, no lo vuelve a crear. Así se puede reiniciar el
contenedor sin duplicar datos. Los datos son FICTICIOS (RF-014).
"""
import datetime
import os
import sys

from proteus import Model, config

DB = os.environ["POSTGRES_DB"]
CONF = os.environ.get("TRYTOND_CONF", "/tmp/trytond.conf")

INSTITUCION = {
    "code": "INST-DEMO",
    "name": "Centro de Salud Demo",
    "institution_type": "primary_care",  # centro de atención primaria
    "public_level": "public",
}

# Pacientes de demostración (ficticios). gender: 'm' / 'f'.
DEMO_PACIENTES = [
    {"name": "Demo Uno Paciente", "gender": "f", "dob": (1970, 5, 12)},
    {"name": "Demo Dos Paciente", "gender": "m", "dob": (1985, 9, 30)},
    {"name": "Demo Tres Paciente", "gender": "f", "dob": (1992, 1, 8)},
]


def ensure_institution(Party, Institution):
    """Crea la institución de salud demo si no existe (idempotente)."""
    if Institution.find([("code", "=", INSTITUCION["code"])]):
        print(f">>   institución ya existe: {INSTITUCION['code']} (se omite)")
        return
    party = Party()
    party.name = INSTITUCION["name"]
    party.is_institution = True
    party.save()

    inst = Institution()
    inst.party = party
    inst.code = INSTITUCION["code"]
    inst.institution_type = INSTITUCION["institution_type"]
    inst.public_level = INSTITUCION["public_level"]
    inst.save()
    print(f">>   institución creada: {INSTITUCION['name']}")


def ensure_health_professional(Party, HealthProf, User):
    """Crea un profesional de salud demo ligado al usuario admin (idempotente).

    Sin un profesional asociado al usuario conectado, GNU Health no permite registrar
    consultas/evaluaciones. Ligarlo al admin deja el sistema usable de una.
    """
    if HealthProf.find([]):
        print(">>   profesional de salud ya existe (se omite)")
        return
    admin = User.find([("login", "=", "admin")])
    party = Party()
    party.name = "Dr. Demo"
    party.is_person = True
    party.is_healthprof = True
    party.gender = "m"
    if admin:
        party.internal_user = admin[0]  # campo "Usuario interno": liga el profesional al login
    party.save()
    hp = HealthProf()
    hp.party = party
    hp.save()
    print(">>   profesional de salud demo creado y ligado a 'admin'")


def ensure_patient(Party, fullname, gender, dob):
    """Crea un paciente si no existe ya uno con ese nombre (idempotente).

    Basta con marcar el party como is_patient=True: GNU Health crea el registro
    gnuhealth.patient automáticamente (crearlo también a mano lo duplicaría).
    """
    if Party.find([("name", "=", fullname)]):
        print(f">>   paciente ya existe: {fullname} (se omite)")
        return
    party = Party()
    party.name = fullname
    party.is_person = True
    party.is_patient = True  # GNU Health auto-crea el gnuhealth.patient
    party.gender = gender
    party.dob = datetime.date(*dob)
    party.save()
    print(f">>   paciente creado: {fullname}")


def main():
    print(f">> Conectando a la base '{DB}' vía proteus ...")
    config.set_trytond(database=DB, config_file=CONF)

    Party = Model.get("party.party")
    Institution = Model.get("gnuhealth.institution")
    Patient = Model.get("gnuhealth.patient")
    HealthProf = Model.get("gnuhealth.healthprofessional")
    User = Model.get("res.user")

    ensure_institution(Party, Institution)
    ensure_health_professional(Party, HealthProf, User)
    for p in DEMO_PACIENTES:
        ensure_patient(Party, p["name"], p["gender"], p["dob"])

    print(f">> Datos de demostración listos. Total pacientes: {len(Patient.find([]))}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — un fallo no debe tumbar el arranque
        print(f">> ERROR cargando datos demo: {exc}", file=sys.stderr)
        sys.exit(1)
