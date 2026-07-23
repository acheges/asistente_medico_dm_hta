"""Cliente agnóstico de proveedor de modelo de lenguaje.

Soporta dos estilos de API por configuración: estilo OpenAI (`/chat/completions`, el que usa Kimi
vía opencode Zen) y estilo Anthropic (`/messages`). El modelo/URL/credencial se eligen por variables
de entorno. Un modo simulado (`AI_DRY_RUN`) permite probar sin llamar al proveedor (cero costo).

La dependencia de red (`requests`) se importa de forma perezosa: así este módulo se puede importar y
probar (armado de peticiones + modo simulado) sin tener `requests` instalado.
"""
import os


class ProveedorError(Exception):
    """Error devuelto por el proveedor del modelo (p. ej. saldo insuficiente, llave inválida)."""

    def __init__(self, mensaje, status):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def _mensaje_error(respuesta):
    """Extrae el mensaje de error legible del cuerpo de la respuesta del proveedor."""
    try:
        cuerpo = respuesta.json()
        return (
            cuerpo.get("error", {}).get("message")
            or cuerpo.get("message")
            or (respuesta.text or "")[:300]
        )
    except Exception:  # noqa: BLE001
        return (respuesta.text or "")[:300]


def config():
    """Lee la configuración del entorno (sin credenciales por defecto)."""
    return {
        "style": os.environ.get("AI_PROVIDER_STYLE", "openai"),
        "base_url": os.environ.get("AI_BASE_URL", "https://opencode.ai/zen/v1"),
        "api_key": os.environ.get("AI_API_KEY", ""),
        "model": os.environ.get("AI_MODEL", "kimi-k2.6"),
        "timeout": float(os.environ.get("AI_TIMEOUT", "30")),
        "dry_run": os.environ.get("AI_DRY_RUN", "false").lower() == "true",
    }


def construir_peticion_openai(system_prompt, user_prompt, cfg):
    """Arma la petición estilo OpenAI (chat/completions)."""
    return {
        "url": cfg["base_url"].rstrip("/") + "/chat/completions",
        "headers": {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        "json": {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
    }


def construir_peticion_anthropic(system_prompt, user_prompt, cfg):
    """Arma la petición estilo Anthropic (messages)."""
    return {
        "url": cfg["base_url"].rstrip("/") + "/messages",
        "headers": {
            "x-api-key": cfg["api_key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        "json": {
            "model": cfg["model"],
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
    }


def _texto_simulado():
    return (
        "[SIMULADO] Interpretación de apoyo: con base en la valoración proporcionada, se comunican "
        "los hallazgos en lenguaje claro para el profesional. Esto es material de APOYO y NO "
        "sustituye el juicio del profesional de la salud."
    )


def generar(system_prompt, user_prompt, cfg=None):
    """Genera el texto de apoyo. Devuelve {"texto": ..., "modelo": ...}."""
    cfg = cfg or config()
    if cfg["dry_run"]:
        return {"texto": _texto_simulado(), "modelo": cfg["model"]}

    import requests  # perezoso: solo se necesita cuando hay llamada real

    if cfg["style"] == "anthropic":
        req = construir_peticion_anthropic(system_prompt, user_prompt, cfg)
    else:  # openai por defecto
        req = construir_peticion_openai(system_prompt, user_prompt, cfg)

    r = requests.post(req["url"], headers=req["headers"], json=req["json"], timeout=cfg["timeout"])
    if r.status_code >= 400:
        # Propaga el mensaje real del proveedor (p. ej. "saldo insuficiente").
        raise ProveedorError(_mensaje_error(r), r.status_code)

    data = r.json()
    if cfg["style"] == "anthropic":
        texto = data["content"][0]["text"]
    else:
        texto = data["choices"][0]["message"]["content"]

    return {"texto": texto, "modelo": cfg["model"]}
