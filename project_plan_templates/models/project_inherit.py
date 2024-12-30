class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Relación con los registros de inventario
    stock_ids = fields.One2many(
        'stock.picking',  # O el modelo que corresponda
        'task_id',  # Relación con el campo en stock.picking que referencia a la tarea
        string="Materiales"
    )
