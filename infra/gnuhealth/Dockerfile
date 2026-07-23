# Imagen PROPIA de GNU Health, construida vía el instalador oficial (pip + gnuhealth-all-modules).
# No es una imagen opaca de terceros (cumple RF-012).
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    VENV=/opt/gnuhealth/venv

# 1. Paquetes de sistema necesarios para compilar las dependencias de GNU Health/Tryton.
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-dev python3-venv \
      build-essential pkg-config \
      libpq-dev libjpeg-dev zlib1g-dev libxml2-dev libxslt1-dev \
      libldap2-dev libsasl2-dev libssl-dev \
      postgresql-client gettext-base curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Usuario no-root y entorno virtual de Python.
RUN useradd -m -d /opt/gnuhealth gnuhealth \
    && python3 -m venv "${VENV}"
ENV PATH="${VENV}/bin:${PATH}"

# 3. Instalar GNU Health con todos sus módulos (el "instalador oficial" vía pip).
#    proteus (misma serie 7.0 que trytond) permite el cargador de datos demo.
RUN pip install --no-cache-dir --upgrade pip wheel setuptools \
    && pip install --no-cache-dir gnuhealth-all-modules "proteus>=7.0,<7.1"

# 4. Cliente web Sao 7.0 (Node.js solo para instalar sus dependencias; trytond lo sirve).
#    Va DESPUÉS del pip para no invalidar la capa cacheada de GNU Health.
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm git \
    && curl -fSL https://downloads.tryton.org/7.0/tryton-sao-last.tgz -o /tmp/sao.tgz \
    && mkdir -p /opt/gnuhealth/sao \
    && tar -xzf /tmp/sao.tgz -C /opt/gnuhealth/sao --strip-components=1 \
    && rm /tmp/sao.tgz \
    && printf '{ "allow_root": true }\n' > /opt/gnuhealth/sao/.bowerrc \
    && ( cd /opt/gnuhealth/sao && npm install --production --legacy-peer-deps ) \
    && chown -R gnuhealth:gnuhealth /opt/gnuhealth/sao \
    && rm -rf /var/lib/apt/lists/*

# 5. Configuración, carpetas y script de arranque.
#    NOTA: el contexto de build es la RAÍZ del repo (ver docker-compose.yml), por eso las
#    rutas de estos archivos incluyen el prefijo infra/gnuhealth/.
RUN mkdir -p /etc/gnuhealth /var/lib/gnuhealth/attach \
    && chown -R gnuhealth:gnuhealth /var/lib/gnuhealth
COPY infra/gnuhealth/trytond.conf /etc/gnuhealth/trytond.conf
COPY infra/gnuhealth/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY infra/gnuhealth/configure.py /usr/local/bin/configure.py
COPY infra/gnuhealth/load_demo.py /usr/local/bin/load_demo.py
RUN chmod +x /usr/local/bin/entrypoint.sh

# 6. Motor de valoración (paquete propio, Feature B) + módulo de captura DM/HTA.
#    El motor se instala en el venv (para `import motor_valoracion`); el módulo se coloca en la
#    carpeta de módulos de trytond para que quede activable (el entrypoint lo incluye por get_modules).
COPY pyproject.toml /tmp/motor/pyproject.toml
COPY motor_valoracion /tmp/motor/motor_valoracion
RUN pip install --no-cache-dir /tmp/motor && rm -rf /tmp/motor
COPY gnuhealth_modules/health_dm_hta \
     ${VENV}/lib/python3.11/site-packages/trytond/modules/health_dm_hta
COPY gnuhealth_modules/health_dm_hta_ia \
     ${VENV}/lib/python3.11/site-packages/trytond/modules/health_dm_hta_ia
COPY gnuhealth_modules/health_dm_hta_ui \
     ${VENV}/lib/python3.11/site-packages/trytond/modules/health_dm_hta_ui

# 7. Personalización global del cliente web Sao (custom.css). Sao lo referencia en su
#    index.html y el servidor lo sirve desde la raíz web. Corrige el amontonamiento de
#    columnas en las listas (ver el propio archivo para el detalle).
COPY infra/gnuhealth/custom.css /opt/gnuhealth/sao/custom.css
COPY infra/gnuhealth/fonts /opt/gnuhealth/sao/fonts

USER gnuhealth
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
