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
        "views/view_project_project_kanban.xml",
        "views/inherit_project_view_form.xml",
        "views/inherit_pickin_form_view.xml",
        "views/inherit_timesheet_view_form.xml",
        "views/inherit_timesheet_line_tree.xml",
        "views/inherit_project_task_form_inherited.xml",
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
