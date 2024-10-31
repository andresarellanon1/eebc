{
    'name': 'Historial de planeacion de proyectos',
    'description': """
            Este modulo comprende la planificacion de proyctos y su historial de versiones.
    """,
    'version': '17.0.0.1',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'project','project_plan_templates'
               ],
    'data': [
        "views/projects_history_view.xml",
        "views/project_history_menu.xml",
        "views/project_history_motive_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}