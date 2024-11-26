from odoo import _, fields, models, api
import logging

logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super(StockMove, self)._action_confirm(merge, merge_into)
        logger.warning(moves)
        return moves
