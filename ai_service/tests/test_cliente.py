"""Pruebas del cliente agnóstico y el prompt (sin red, proveedor simulado)."""
from ai_service import cliente_llm, prompt

_CFG = {
    "style": "openai",
    "base_url": "https://opencode.ai/zen/v1",
    "api_key": "sk-demo",
    "model": "kimi-k2.6",
    "timeout": 30,
    "dry_run": False,
}


def test_peticion_openai_formato():
    req = cliente_llm.construir_peticion_openai("SYS", "USR", _CFG)
    assert req["url"].endswith("/chat/completions")
    assert req["headers"]["Authorization"] == "Bearer sk-demo"
    assert req["json"]["model"] == "kimi-k2.6"
    roles = [m["role"] for m in req["json"]["messages"]]
    assert roles == ["system", "user"]


def test_peticion_anthropic_formato():
    cfg = dict(_CFG, style="anthropic")
    req = cliente_llm.construir_peticion_anthropic("SYS", "USR", cfg)
    assert req["url"].endswith("/messages")
    assert req["headers"]["x-api-key"] == "sk-demo"
    assert req["json"]["system"] == "SYS"
    assert req["json"]["messages"][0]["role"] == "user"
    assert "max_tokens" in req["json"]


def test_generar_modo_simulado_no_usa_red():
    cfg = dict(_CFG, dry_run=True)
    r = cliente_llm.generar("SYS", "USR", cfg)
    assert r["modelo"] == "kimi-k2.6"
    assert "no sustituye" in r["texto"].lower()


def test_prompt_fija_rol_de_apoyo():
    sys_p, user_p = prompt.construir({"version": "1", "valoracion": {"x": 1}})
    assert "NO diagnostiques" in sys_p
    assert "apoyo" in sys_p.lower()
    assert "valoración estructurada" in user_p.lower()
