"""Aduana: construye el payload LIMPIO de egreso a partir de los datos de una evaluación.

Es código DETERMINISTA y auditable (no interviene ningún modelo). Estructurada como un pipeline de
pasos; hoy: valoración + edad/sexo. Nunca incluye datos de identificación personal: un validador
"prohibido PII" FALLA CERRADA (bloquea el egreso si detecta un campo prohibido).
"""
import uuid

VERSION = "1"

# Nombres de campo prohibidos en el payload (en cualquier nivel). Falla cerrada.
CAMPOS_PROHIBIDOS = {
    "nombre", "name", "curp", "direccion", "address", "telefono", "phone",
    "email", "correo", "dob", "fecha_nacimiento", "identificador", "ref", "party",
    "rec_name", "internal_user", "ssn",
}


def token_efimero():
    """Token opaco por solicitud; se descarta tras re-ligar la respuesta."""
    return "req-" + uuid.uuid4().hex


def _validar_sin_pii(obj, ruta=""):
    """Recorre el payload y lanza ValueError si aparece un campo prohibido (falla cerrada)."""
    if isinstance(obj, dict):
        for clave, valor in obj.items():
            if str(clave).lower() in CAMPOS_PROHIBIDOS:
                raise ValueError(f"Egreso bloqueado: campo prohibido (PII) en el payload: {ruta}{clave}")
            _validar_sin_pii(valor, f"{ruta}{clave}.")
    elif isinstance(obj, list):
        for item in obj:
            _validar_sin_pii(item, ruta)


def construir_payload(datos, des_identificacion_total=False):
    """Construye el payload seudonimizado.

    `datos`: dict con `edad`, `sexo`, `valoracion` (dict). Devuelve (payload, campos_enviados).
    `des_identificacion_total`: interruptor listo para dejar fuera extras futuros (p. ej. historial).
    """
    # Paso 1 — identidad no identificatoria (solo edad y sexo).
    paciente = {"edad": datos.get("edad"), "sexo": datos.get("sexo")}

    # Paso 2 — la valoración estructurada (ya viene sin PII del motor determinista).
    valoracion = datos.get("valoracion") or {}

    # (Futuro) Paso 3 — síntomas/historial pasarían aquí por su propio paso de redacción.
    #           Con des_identificacion_total=True, esos extras se omiten.

    payload = {
        "version": VERSION,
        "token": token_efimero(),
        "paciente": paciente,
        "valoracion": valoracion,
    }

    # Validación final: falla cerrada si hubiera PII.
    _validar_sin_pii(payload)

    campos_enviados = "paciente.edad, paciente.sexo, valoracion"
    return payload, campos_enviados
