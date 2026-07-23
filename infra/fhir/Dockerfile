# Servidor FHIR de GNU Health — OPCIONAL y de SOLO LECTURA.
#
# ⚠️ EXPERIMENTAL: gnuhealth-fhir-server es beta (0.9b7, últ. actualización 2023) y
#    puede NO ser compatible con GNU Health 5.0 / trytond 7.0 (ver research.md, Decisión 4).
#    Por eso va apagado por defecto (perfil "fhir") y NO bloquea el despliegue principal.
#    La vía principal de datos es la API JSON-RPC de trytond, no FHIR.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    VENV=/opt/fhir/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-dev python3-venv \
      build-essential libpq-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv "${VENV}"
ENV PATH="${VENV}/bin:${PATH}"

# Instalación tolerante: si el paquete beta no resuelve, no rompe el build de la imagen.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir gnuhealth-fhir-server \
    || echo "AVISO: gnuhealth-fhir-server no instaló limpio (componente beta)."

EXPOSE 8080

# Servicio experimental: el arranque real requiere configurar el servidor FHIR contra
# trytond. Mientras se difiere (research.md Decisión 4), mantiene el contenedor vivo
# para inspección manual sin bloquear el resto del stack.
CMD ["sh", "-c", "echo 'Servidor FHIR opcional (EXPERIMENTAL). Configurar contra trytond antes de usar. Ver docs/despliegue-vps.md'; sleep infinity"]
