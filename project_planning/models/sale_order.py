from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import logging
logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Es proyecto?", default=False)
    project_name = fields.Char(string="Titulo de proyecto")
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    state = fields.Selection(
        selection_add=[
            ('budget', 'Budget'),
            ('process', 'In process')
        ],
        ondelete={
            'budget': 'set default',
            'process': 'set default'
        }
    )

    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id')

    project_id = fields.Many2one('project.project', string="Proyecto")

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.onchange('is_project')
    def _onchange_is_project(self):
        for record in self:
            record.order_line = None