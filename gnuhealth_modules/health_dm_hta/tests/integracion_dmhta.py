#!/usr/bin/env python3
"""Prueba de integración de health_dm_hta contra GNU Health desplegado.

Crea una evaluación de comorbilidad, dispara el cálculo por el botón de la vista (dmhta_calcular)
y verifica que la valoración PERSISTE. Ejercita la función real (escribir/operar), no solo lectura.

Ejecutar dentro del contenedor:
    /opt/gnuhealth/venv/bin/python3 \
      /opt/gnuhealth/venv/lib/python3.11/site-packages/trytond/modules/health_dm_hta/tests/integracion_dmhta.py

Requiere: Feature A desplegada, módulo health_dm_hta activado, y un profesional de salud ligado
al usuario admin (lo crea el cargador de datos demo, load_demo.py).
"""
import os
import sys

from proteus import Model, config

DB = os.environ.get("POSTGRES_DB", "gnuhealth")
CONF = os.environ.get("TRYTOND_CONF", "/tmp/trytond.conf")
config.set_trytond(database=DB, config_file=CONF)

Patient = Model.get("gnuhealth.patient")
Evaluation = Model.get("gnuhealth.patient.evaluation")

pacientes = Patient.find([], limit=1)
if not pacientes:
    print("ERROR: no hay pacientes (¿corriste el cargador demo?).", file=sys.stderr)
    sys.exit(1)

ev = Evaluation()
ev.patient = pacientes[0]
ev.systolic = 150
ev.diastolic = 95
ev.bmi = 27.0
ev.glycemia = 130.0
ev.dmhta_perimetro_cintura = 88.0
ev.dmhta_actividad_fisica = True
ev.dmhta_verduras_frutas = True
ev.dmhta_medicacion_antihipertensiva = False
ev.dmhta_antecedente_glucosa_alta = True
ev.dmhta_antecedente_familiar = "segundo_grado"
ev.dmhta_catalogo = "estandar"
ev.save()

# Antes de calcular, NO es una valoración DM/HTA (la marca debe estar apagada) — Feature D.
ev.reload()
assert ev.dmhta_es_valoracion is False, "la marca no debería estar encendida antes de calcular"

ev.click("dmhta_calcular")  # dispara el motor por el botón de la vista
ev.reload()

assert ev.dmhta_findrisc_categoria, "FINDRISC no calculado"
assert ev.dmhta_ta_categoria == "Hipertensión etapa 2", ev.dmhta_ta_categoria
assert ev.dmhta_glucosa_interpretacion == "Rango de diabetes", ev.dmhta_glucosa_interpretacion
assert ev.dmhta_valoracion_estructurada, "JSON estructurado no persistido"
# Tras calcular, la marca queda encendida: ahora aparecerá en la lista propia (Feature D).
assert ev.dmhta_es_valoracion is True, "la marca debería encenderse al calcular"

print(
    "OK integración: FINDRISC=%s (%s) | TA=%s | glucosa=%s | JSON=%d chars"
    % (
        ev.dmhta_findrisc_puntaje,
        ev.dmhta_findrisc_categoria,
        ev.dmhta_ta_categoria,
        ev.dmhta_glucosa_interpretacion,
        len(ev.dmhta_valoracion_estructurada),
    )
)
