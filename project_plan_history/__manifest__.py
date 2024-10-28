{
    'name': 'Historial de planeacion de proyectos',
    'description': """
            Este modulo comprende la planificacion de proyctos y su historial de versiones.
    """,
    'version': '17.0.0.1',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'project'
               ],
    'data': [
        "views/projects_history_view.xml",
        "views/project_history_menu.xml",
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}