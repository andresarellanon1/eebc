from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"


  
    notice_file_wizard_id = fields.Many2one(
        comodel_name='notice.file.wizard',
        string='Supplier'
        
    )
    
   