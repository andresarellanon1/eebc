from odoo import _, fields, models, api
import logging

logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super(StockMove, self)._action_confirm()

        for move in moves:
            logger.warning(move)

        return moves
    #     for move in moves:
    #         if move.purchase_id and move.purchase_id.
