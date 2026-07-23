#!/usr/bin/env python3
"""Configuración post-instalación de GNU Health (idempotente, se ejecuta SIEMPRE).

Aplica el idioma de la interfaz (GNUHEALTH_LANG) al usuario administrador. Cargar las
traducciones (`trytond-admin -l`) solo las deja DISPONIBLES; la interfaz toma el idioma de
la preferencia de cada usuario, así que hay que fijárselo al admin explícitamente.
"""
import os
import sys

from proteus import Model, config

DB = os.environ["POSTGRES_DB"]
CONF = os.environ.get("TRYTOND_CONF", "/tmp/trytond.conf")
LANG = os.environ.get("GNUHEALTH_LANG", "es_419")


def main():
    config.set_trytond(database=DB, config_file=CONF)
    Lang = Model.get("ir.lang")
    User = Model.get("res.user")

    langs = Lang.find([("code", "=", LANG)])
    if not langs:
        print(f">>   AVISO: el idioma '{LANG}' no existe en ir.lang; se omite.")
        return
    lang = langs[0]

    # Asegurar que el idioma esté activo y sea traducible.
    changed = False
    if not lang.active:
        lang.active = True
        changed = True
    if not lang.translatable:
        lang.translatable = True
        changed = True
    if changed:
        lang.save()

    # Fijar el idioma al usuario admin (idempotente).
    admins = User.find([("login", "=", "admin")])
    if not admins:
        print(">>   AVISO: no se encontró el usuario 'admin'; se omite el idioma.")
        return
    adm = admins[0]
    if not adm.language or adm.language.code != LANG:
        adm.language = lang
        adm.save()
        print(f">>   idioma de la interfaz (admin) fijado a '{LANG}'.")
    else:
        print(f">>   idioma de la interfaz (admin) ya es '{LANG}'.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — un fallo aquí no debe tumbar el arranque
        print(f">> AVISO: no se pudo configurar el idioma: {exc}", file=sys.stderr)
        sys.exit(0)
