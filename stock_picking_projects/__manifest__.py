{
    'name': 'Stock Picking Projects',
    'description': """
            Este modulo comprende las configuraciones de.
    """,
    'version': '17.0.0.01',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'stock','project'
               ],
    'data': [
        "views/inherit_project_task_view_form.xml",
        "views/view_project_project_kanban.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
