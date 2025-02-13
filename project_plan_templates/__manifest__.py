{
    'name': 'Planeación de proyectos',
    'summary': 'Gestión de tareas, productos e inventarios.',
    'description': """
            Este módulo de Odoo facilita la gestión de tareas, productos y logística en proyectos. Permite asignar productos a tareas, 
            controlar el inventario y calcular las horas de trabajo necesarias. Además, automatiza los movimientos de stock entre 
            ubicaciones, optimizando la logística interna.
    """,
    'version': '17.0.1.001',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'project', 'product', 'sale', 'sale_project'
    ],
    'data': [
        "reports/report_analytics.xml",
        "reports/report_definition.xml",
        "security/ir.model.access.csv",
        "views/inherit_product_template_view.xml",
        "views/inherit_project_task_form_inherited2.xml",
        "views/inherit_project_task_inventory_view_form.xml",
        "views/inherit_sale_order_view_form.xml",
        "views/inherit_sale_project_view.xml",
        "views/inherit_task_view_form.xml",
        "views/inherit_timesheet_view_form.xml",
        "views/plan_picking_template_view.xml",
        "views/plan_project_stock_tree_view.xml",
        "views/plan_template_view.xml",
        "views/project_menu.xml",
        "views/task_picking_line.xml",
        "views/timesheet_template_view.xml",
        "views/inherit_sale_order_tree.xml",
        "views/inherit_sale_order_line_form.xml"
        "wizard/view_project_creation_wizard_form.xml",
        "wizard/view_task_inventory_wizard.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
    "application": True,
}
