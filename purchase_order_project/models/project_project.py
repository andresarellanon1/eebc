from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = "project.project"

    purchase_ids = fields.Many2many(comodel_name='purchase.order', string='Compras')