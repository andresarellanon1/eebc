{
    'name': 'Historial de moficaciones de proyectos',
    'description': """
            Este modulo comprende el historial para cambios en los proyectos.
    """,
    'version': '17.0.0.1',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'project','project_plan_templates'
               ],
    'data': [
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}