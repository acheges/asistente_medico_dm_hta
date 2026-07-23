# Thalamus — hub REST de la Federación de GNU Health. OPCIONAL y EXPERIMENTAL.
#
# ⚠️ Su valor pleno llega con la Federación (multi-nodo), que está FUERA de alcance de
#    esta feature (ver research.md, Decisión 5). Además requiere MongoDB.
#    Va apagado por defecto (perfil "thalamus") y "listo para encender" en el futuro.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    VENV=/opt/thalamus/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-dev python3-venv \
      build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv "${VENV}"
ENV PATH="${VENV}/bin:${PATH}"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir thalamus \
    || echo "AVISO: thalamus no instaló limpio (requiere revisión; fase Federación)."

EXPOSE 8443

# Servicio experimental: Thalamus necesita MongoDB y configuración de Federación.
# Se deja listo para encender; mientras, mantiene el contenedor vivo sin bloquear el stack.
CMD ["sh", "-c", "echo 'Thalamus opcional (EXPERIMENTAL). Requiere MongoDB + config de Federación. Ver docs/despliegue-vps.md'; sleep infinity"]
