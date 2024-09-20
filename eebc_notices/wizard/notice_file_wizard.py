# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
class NoticeFileWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "notice.file.wizard"
    _description = "Wizard to recover data from xlsx file"

    file_xlsx = fields.Binary(string="Archivo" )
    name = fields.Char(string="Nombre")
    quantity = fields.Float(string="Cantidad")
    def action_data_analysis(self):
        
        _logger.warning('Entramos a action_data_analysis')
        _logger.warning(f"Nombre del archivo: {self.file_xlsx}")
        _logger.warning(f"Nombre del wizard: {self.name}")
        _logger.warning(f"Cantidad: {self.quantity}")







