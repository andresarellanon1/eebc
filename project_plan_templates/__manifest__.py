{
    'name': 'Plantillas para planeacion de proyectos',
    'description': """
            Este modulo comprende las configuraciones para la generacion de plantillas de proyectos.
    """,
    'version': '17.0.0.01',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                
               ],
    'data': [
        "views/project_menu.xml",
        "views/plan_template_view.xml",
        "security/ir.model.access.csv",
        "views/inherit_timesheet_view_form.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
