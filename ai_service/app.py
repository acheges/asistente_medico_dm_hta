"""ai-service: endpoint HTTP. Recibe payload limpio → devuelve texto. Ciego a la identidad."""
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_service import cliente_llm, prompt
from ai_service.cliente_llm import ProveedorError

app = FastAPI(title="ai-service (asistente intérprete)")


class Payload(BaseModel):
    version: str
    token: Optional[str] = None
    paciente: Optional[dict] = None
    valoracion: Optional[dict] = None


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/interpretar")
def interpretar(payload: Payload):
    system_prompt, user_prompt = prompt.construir(payload.model_dump())
    try:
        return cliente_llm.generar(system_prompt, user_prompt)
    except ProveedorError as exc:
        # Devuelve el mensaje real del proveedor para que la aduana lo muestre al profesional.
        raise HTTPException(status_code=502, detail=exc.mensaje)
