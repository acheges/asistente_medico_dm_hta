#!/usr/bin/env bash
# Checklist de encendido del contenedor de GNU Health.
set -euo pipefail

echo ">> Esperando a la base de datos en ${DB_HOST}:${DB_PORT} ..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  sleep 2
done
echo ">> Base de datos lista."

# 0. Validar credenciales del administrador (RF-011: sin credenciales por defecto inseguras).
if [ -z "${ADMIN_PASSWORD:-}" ]; then
  echo ">> ERROR: ADMIN_PASSWORD está vacío. Define una contraseña en infra/.env." >&2
  exit 1
fi
if [ "${ADMIN_PASSWORD}" = "cambia_esto_en_local" ]; then
  echo ">> AVISO: ADMIN_PASSWORD tiene el valor de ejemplo (OK para local; CÁMBIALO antes de un VPS)." >&2
fi

# 1. Renderizar la configuración sustituyendo las variables ${...} del entorno.
TRYTOND_CONF=/tmp/trytond.conf
envsubst < /etc/gnuhealth/trytond.conf > "${TRYTOND_CONF}"
export TRYTOND_CONF

# 2. Archivo temporal con la contraseña del admin (lo consume trytond-admin).
export TRYTONPASSFILE=/tmp/adminpass
printf '%s' "${ADMIN_PASSWORD}" > "${TRYTONPASSFILE}"

# 3. Inicializar / activar / actualizar GNU Health (idempotente: se puede repetir).
#    Se activan TODOS los módulos disponibles (GNU Health completo). En una base nueva
#    `--all` NO basta (solo actualiza lo ya activado); por eso se listan los módulos con -u.
#    --activate-dependencies resuelve dependencias entre módulos.
#    -p fija la contraseña del admin (desde TRYTONPASSFILE); -l carga el idioma de .env.
# health_federation queda FUERA (federación multi-nodo = fase 2, fuera de alcance):
# encola un registro de sincronización en cada guardado y exige institución de federación,
# lo que estorba la operación local. Se puede reactivar cuando la federación entre en alcance.
GNUHEALTH_EXCLUDE="health_federation"
GNUHEALTH_MODULES="$(python3 -c "from trytond.modules import get_modules; excl={'${GNUHEALTH_EXCLUDE}'}; print(' '.join(sorted(m for m in get_modules() if m not in excl)))")"
echo ">> Activando/actualizando GNU Health (idioma: ${GNUHEALTH_LANG:-es_419}) ..."
echo ">>   módulos: ${GNUHEALTH_MODULES}"
# --email evita el prompt interactivo del correo del admin (que en base nueva pediría
# por teclado y, sin TTY, rompería con EOFError).
# shellcheck disable=SC2086  # queremos que la lista de módulos se expanda en palabras.
trytond-admin -c "${TRYTOND_CONF}" -d "${POSTGRES_DB}" \
  -u ${GNUHEALTH_MODULES} --activate-dependencies \
  -p --email "${ADMIN_EMAIL:-admin@localhost}" -v -l "${GNUHEALTH_LANG:-es_419}"

# 4. Configuración post-instalación (siempre): fijar el idioma de la interfaz al admin.
echo ">> Configurando idioma de la interfaz ..."
python3 /usr/local/bin/configure.py \
  || echo ">> AVISO: no se pudo configurar el idioma (no bloquea el arranque)." >&2

# 5. (Opcional) Datos de demostración: pacientes ficticios (idempotente).
#    Se controla con LOAD_DEMO_DATA en .env. No bloquea el arranque si falla.
if [ "${LOAD_DEMO_DATA:-false}" = "true" ]; then
  echo ">> LOAD_DEMO_DATA=true — cargando pacientes de demostración ..."
  python3 /usr/local/bin/load_demo.py \
    || echo ">> AVISO: la carga de datos demo falló (no bloquea el arranque)." >&2
fi

# 6. Quitar el archivo de contraseña.
rm -f "${TRYTONPASSFILE}"

# 7. Arrancar el servidor de GNU Health (sirve la API JSON-RPC y el web en :8000).
echo ">> Iniciando GNU Health en el puerto 8000 ..."
exec trytond -c "${TRYTOND_CONF}"
