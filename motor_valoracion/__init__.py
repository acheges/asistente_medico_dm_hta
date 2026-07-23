"""motor_valoracion — motor determinista de valoración DM2 + HTA.

Paquete de Python PURO (sin Tryton, sin base de datos, sin interfaz): entra un diccionario de
datos, sale un resultado estructurado. Agnóstico de consumidor: lo usa la interfaz de GNU Health
hoy y podrá usarlo el modelo de lenguaje (Feature C) mañana.

Ver el contrato en specs/002-captura-valoracion-dm-hta/contracts/motor-valoracion.md
"""
from .valoracion import valorar

__all__ = ["valorar"]
