{
    'name': 'Historial de moficaciones de proyectos',
    'description': """
            Este modulo comprende el historial para cambios en los proyectos.
    """,
    'version': '17.0.1.001',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'project', 'project_plan_templates'
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/menus.xml",
        "views/project_version_history_view.xml",
        "views/inherit_project_task_form_version.xml",
        "views/project_version_view.xml",
        "wizard/view_version_creation_wizard_form.xml",
        "views/inherit_project_edit_view.xml",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
