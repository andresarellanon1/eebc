{
    'name': 'Plantillas para planeacion de proyectos',
    'description': """
            Este modulo comprende las configuraciones para la generacion de plantillas de proyectos.
    """,
    'version': '17.0.0.02',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'project', 'product', 'sale'
               ],
    'data': [
        "views/project_menu.xml",
        "views/plan_template_view.xml",
        "security/ir.model.access.csv",
        "views/inherit_timesheet_view_form.xml",
        "views/inherit_task_view_form.xml",
        "views/plan_picking_template_view.xml",
        "wizard/view_project_creation_wizard_form.xml",
        "views/timesheet_template_view.xml",
        "views/inherit_project_task_form_inherited2.xml",
        "views/plan_project_stock_tree_view.xml",
        "wizard/view_task_inventory_wizard.xml",
        "views/inherit_project_task_inventory_view_form.xml",
        "views/task_picking_line.xml",
        "views/inherit_sale_order_view_form.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
