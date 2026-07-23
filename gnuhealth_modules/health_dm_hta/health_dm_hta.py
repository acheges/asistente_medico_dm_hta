"""Extensión de la evaluación de GNU Health para la comorbilidad DM2 + HTA."""
import datetime
import json
import os

from trytond.model import ModelView, fields
from trytond.pool import PoolMeta

try:  # el motor es un paquete propio instalado en la imagen
    from motor_valoracion import valorar
except Exception:  # pragma: no cover - si no está instalado, el módulo no rompe
    valorar = None


_FAMILIAR = [
    ("no", "Sin antecedentes"),
    ("segundo_grado", "Familiar de segundo grado (abuelos, tíos, primos)"),
    ("primer_grado", "Familiar de primer grado (padres, hermanos, hijos)"),
]

_CATALOGO = [
    ("estandar", "Estándar internacional"),
    ("nom", "Normas mexicanas (NOM-015 / NOM-030)"),
]


class PatientEvaluation(metaclass=PoolMeta):
    __name__ = "gnuhealth.patient.evaluation"

    # --- Reactivos FINDRISC que GNU Health no captura de fábrica ---
    dmhta_perimetro_cintura = fields.Float("Perímetro de cintura (cm)")
    dmhta_actividad_fisica = fields.Boolean("Actividad física ≥30 min al día")
    dmhta_verduras_frutas = fields.Boolean("Consumo diario de verduras y frutas")
    dmhta_medicacion_antihipertensiva = fields.Boolean("Toma medicación antihipertensiva")
    dmhta_antecedente_glucosa_alta = fields.Boolean("Antecedente de glucosa elevada")
    dmhta_antecedente_familiar = fields.Selection(
        _FAMILIAR, "Antecedente familiar de diabetes"
    )

    # --- Configuración: catálogo de umbrales ---
    dmhta_catalogo = fields.Selection(_CATALOGO, "Catálogo de umbrales")

    # --- Resultado de la valoración (calculado por el motor) ---
    dmhta_findrisc_puntaje = fields.Integer("Puntaje FINDRISC", readonly=True)
    dmhta_findrisc_categoria = fields.Char("Riesgo de diabetes (FINDRISC)", readonly=True)
    dmhta_ta_categoria = fields.Char("Clasificación de tensión arterial", readonly=True)
    dmhta_glucosa_interpretacion = fields.Char("Interpretación de glucosa", readonly=True)
    dmhta_valoracion_estructurada = fields.Text(
        "Valoración estructurada (JSON)", readonly=True
    )
    dmhta_editado_por_humano = fields.Boolean("Valoración editada por el profesional")

    # --- Marca: ¿esta evaluación es una valoración DM/HTA? (Feature D) ---
    # La enciende el sistema al calcular. Permite listar solo las valoraciones DM/HTA sin mezclar
    # consultas ajenas (RF-018). Vive en el módulo base porque es metadato, no presentación.
    dmhta_es_valoracion = fields.Boolean("¿Es valoración DM/HTA?", readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        # Habilita el botón "Calcular valoración" en la vista.
        cls._buttons.update({"dmhta_calcular": {}})

    @staticmethod
    def default_dmhta_antecedente_familiar():
        return "no"

    @staticmethod
    def default_dmhta_es_valoracion():
        return False

    @staticmethod
    def default_dmhta_catalogo():
        # Configurable por variable de entorno (RF-013); por defecto, estándar internacional.
        return os.environ.get("DMHTA_CATALOGO", "estandar")

    # --- Cálculo de la valoración ---
    def _dmhta_edad(self):
        party = getattr(self.patient, "party", None) if self.patient else None
        dob = getattr(party, "dob", None) if party else None
        if not dob:
            return None
        return int((datetime.date.today() - dob).days // 365.25)

    def _dmhta_sexo(self):
        party = getattr(self.patient, "party", None) if self.patient else None
        return getattr(party, "gender", None) if party else None

    def _dmhta_imc(self):
        """IMC de la evaluación; si viene vacío, se calcula desde peso y talla (talla en cm).

        GNU Health normalmente llena el IMC con un on_change del formulario; en la pantalla
        propia ese cálculo puede no dispararse. Al Calcular lo derivamos aquí para que el
        FINDRISC no quede sin puntaje por un IMC ausente. Es determinista, no inventa dato.
        """
        if self.bmi:
            return self.bmi
        peso, talla = self.weight, self.height
        if peso and talla:
            metros = float(talla) / 100.0
            if metros > 0:
                return round(float(peso) / (metros * metros), 1)
        return None

    def _dmhta_entrada(self):
        """Arma el diccionario de entrada del motor a partir de la evaluación."""
        return {
            "paciente": {"edad": self._dmhta_edad(), "sexo": self._dmhta_sexo()},
            "antropometria": {
                "imc": self._dmhta_imc(),
                "perimetro_cintura_cm": self.dmhta_perimetro_cintura,
            },
            "signos": {
                "ta_sistolica_mmhg": self.systolic,
                "ta_diastolica_mmhg": self.diastolic,
            },
            "laboratorio": {"glucosa_ayuno_mgdl": self.glycemia},
            "findrisc": {
                "actividad_fisica_diaria": self.dmhta_actividad_fisica,
                "consumo_verduras_frutas_diario": self.dmhta_verduras_frutas,
                "medicacion_antihipertensiva": self.dmhta_medicacion_antihipertensiva,
                "antecedente_glucosa_elevada": self.dmhta_antecedente_glucosa_alta,
                "antecedente_familiar_diabetes": self.dmhta_antecedente_familiar,
            },
            "catalogo": self.dmhta_catalogo or "estandar",
        }

    def _dmhta_aplicar(self, resultado):
        """Vuelca el resultado estructurado del motor en los campos de la evaluación."""
        self.dmhta_valoracion_estructurada = json.dumps(
            resultado, ensure_ascii=False, indent=2
        )
        self.dmhta_catalogo = resultado.get("catalogo", self.dmhta_catalogo)
        for c in resultado.get("conclusiones", []):
            if c["dominio"] == "riesgo_diabetes_findrisc":
                self.dmhta_findrisc_puntaje = c["valor"]["puntaje"]
                self.dmhta_findrisc_categoria = c["etiqueta"]
            elif c["dominio"] == "tension_arterial":
                self.dmhta_ta_categoria = c["etiqueta"]
            elif c["dominio"] == "glucosa_ayuno":
                self.dmhta_glucosa_interpretacion = c["etiqueta"]

    @classmethod
    @ModelView.button
    def dmhta_calcular(cls, evaluations):
        """Calcula la valoración determinista para las evaluaciones dadas y la guarda."""
        if valorar is None:
            return
        for ev in evaluations:
            imc = ev._dmhta_imc()
            if imc and not ev.bmi:  # deja el IMC calculado visible en el campo
                ev.bmi = imc
            ev._dmhta_aplicar(valorar(ev._dmhta_entrada()))
            ev.dmhta_es_valoracion = True  # marca: ya es una valoración DM/HTA (Feature D)
        cls.save(evaluations)
