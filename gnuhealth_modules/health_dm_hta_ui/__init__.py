"""Módulo health_dm_hta_ui: pantalla clínica propia DM/HTA (presentación y recorrido).

No define modelos ni campos nuevos: aporta SOLO artefactos de interfaz sobre el modelo existente
`gnuhealth.patient.evaluation` — una vista de árbol (lista/panel longitudinal), una vista de
formulario propia y limpia, y las acciones/menú/relate para llegar a ellas por dos puertas
(menú "Salud → DM/HTA" y acción relacionada desde el paciente).

La marca `dmhta_es_valoracion` que filtra la lista vive en el módulo base `health_dm_hta`.
"""
from trytond.pool import Pool


def register():
    # Sin modelos propios: la feature es de vistas y acciones (definidas en los XML declarados
    # en tryton.cfg). El register() debe existir aunque no registre nada.
    Pool.register(
        module="health_dm_hta_ui",
        type_="model",
    )
