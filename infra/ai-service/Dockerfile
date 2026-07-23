# ai-service — asistente de lenguaje intérprete (CIEGO a la identidad).
# Contenedor mínimo, sin estado. Recibe payload seudonimizado → devuelve texto.
# El contexto de build es la RAÍZ del repo (ver docker-compose.yml) para incluir ai_service/.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY ai_service/requirements.txt /app/ai_service/requirements.txt
RUN pip install --no-cache-dir -r /app/ai_service/requirements.txt

COPY ai_service /app/ai_service

EXPOSE 8080
CMD ["uvicorn", "ai_service.app:app", "--host", "0.0.0.0", "--port", "8080"]
