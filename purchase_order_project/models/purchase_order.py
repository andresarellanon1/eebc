from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_ids = fields.Many2many(comodel_name='project.project', string='Projectos')