"""Extensión de la evaluación para la interpretación con IA (la aduana) + bitácora de egreso."""
import datetime
import json
import os
import urllib.error
import urllib.request

from trytond.exceptions import UserError
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta

from . import aduana


class PatientEvaluation(metaclass=PoolMeta):
    __name__ = "gnuhealth.patient.evaluation"

    # Resultado de la interpretación con IA.
    dmhta_ia_texto = fields.Text("Interpretación de apoyo (IA)")
    dmhta_ia_texto_editado = fields.Boolean("Texto editado por el profesional")
    dmhta_ia_modelo = fields.Char("Modelo utilizado", readonly=True)
    dmhta_ia_fecha = fields.DateTime("Fecha de la interpretación", readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({"dmhta_ia_interpretar": {}})

    # --- Bitácora de egreso (sin identidad) ---
    def _dmhta_ia_bitacora(self, token, campos, modelo, resultado):
        Egreso = Pool().get("gnuhealth.dm_hta.ia_egreso")
        Egreso.create([{
            "token": token,
            "campos_enviados": campos,
            "fecha": datetime.datetime.now(),
            "modelo": modelo or "",
            "resultado": resultado,
        }])

    def _dmhta_ia_interpretar_uno(self):
        if not self.dmhta_valoracion_estructurada:
            raise UserError(
                "No hay valoración que interpretar. Calcula primero la valoración (botón "
                "'Calcular valoración') antes de pedir la interpretación con IA."
            )

        valoracion = json.loads(self.dmhta_valoracion_estructurada)
        datos = {
            "edad": self._dmhta_edad(),
            "sexo": self._dmhta_sexo(),
            "valoracion": valoracion,
        }
        total = os.environ.get("AI_DESID_TOTAL", "false").lower() == "true"

        # ADUANA: construye el payload LIMPIO (falla cerrada si hubiera PII).
        payload, campos = aduana.construir_payload(datos, des_identificacion_total=total)

        url = os.environ.get("AI_SERVICE_URL", "http://ai-service:8080").rstrip("/") + "/interpretar"
        timeout = float(os.environ.get("AI_TIMEOUT", "30"))
        modelo = None
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            texto = data.get("texto")
            modelo = data.get("modelo")
        except urllib.error.HTTPError as exc:
            # El ai-service alcanzó al proveedor pero éste rechazó la petición (p. ej. saldo
            # insuficiente, llave inválida). Se muestra el mensaje real. NADA clínico egresó de más.
            detalle = ""
            try:
                detalle = json.loads(exc.read().decode("utf-8")).get("detail", "")
            except Exception:  # noqa: BLE001
                detalle = ""
            raise UserError(
                "El asistente de IA no pudo generar la interpretación (el proveedor rechazó la "
                f"petición). {detalle or f'Error {exc.code}.'}"
            )
        except (urllib.error.URLError, OSError, ValueError) as exc:
            # Servicio apagado/inalcanzable: NADA egresó. Se informa y el expediente queda intacto
            # (el UserError revierte la transacción). No se registra bitácora (no hubo envío completado).
            raise UserError(
                "El asistente de IA no está disponible. Verifica que el servicio 'ai-service' esté "
                f"activo (perfil 'ia'). Detalle: {exc}"
            )

        # Re-identificación: el resultado se liga a ESTA evaluación (dentro de la zona de confianza).
        self.dmhta_ia_texto = texto
        self.dmhta_ia_modelo = modelo
        self.dmhta_ia_fecha = datetime.datetime.now()
        self.dmhta_ia_texto_editado = False
        self._dmhta_ia_bitacora(payload["token"], campos, modelo, "ok")

    @classmethod
    @ModelView.button
    def dmhta_ia_interpretar(cls, evaluations):
        """Pide al ai-service la interpretación de apoyo y la guarda (una por evaluación)."""
        for ev in evaluations:
            ev._dmhta_ia_interpretar_uno()
        cls.save(evaluations)


class IaEgreso(ModelSQL, ModelView):
    "Bitácora de egreso al asistente de IA (sin identidad)"
    __name__ = "gnuhealth.dm_hta.ia_egreso"

    token = fields.Char("Token de la solicitud", readonly=True)
    campos_enviados = fields.Text("Campos enviados", readonly=True)
    fecha = fields.DateTime("Fecha y hora", readonly=True)
    modelo = fields.Char("Modelo utilizado", readonly=True)
    resultado = fields.Selection(
        [("ok", "OK"), ("error", "Error")], "Resultado", readonly=True
    )
