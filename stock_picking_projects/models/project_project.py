from odoo import models, fields, api

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many(
        'stock.picking',
        string="Operaciones de Inventario", 
        domain="[('id', 'in', pickin_ids)]"
    )

    @api.depends('id')
    def _compute_pickin_ids(self):
        for project in self:
            project_tasks = self.env['project.task'].search([('project_id', '=', project.id)])
            
            task_picking_ids = self.env['stock.picking'].search([
                ('task_id', 'in', project_tasks.ids)
            ])
            
            project.pickin_ids = task_picking_ids