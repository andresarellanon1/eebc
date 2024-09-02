from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class AccountMoveSendMail(models.TransientModel):
    _name = 'account.move.send'
    _inherit = 'account.move.send'
    _description = "Account Move Send"

    mail_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Recipients",
        readonly=False,
    )

    partner_domain_ids = fields.One2many(
        comodel_name='res.partner',
        compute='_compute_partner_domain_ids',
        store=False,
    )

    @api.depends('move_ids', 'company_id')
    def _compute_partner_domain_ids(self):
        for record in self:
            partner_ids = record.move_ids.mapped('partner_id.id')
            child_ids = record.move_ids.mapped('partner_id.child_ids.id')
            company_partner_id = record.company_id.partner_id.id if record.company_id and record.company_id.partner_id else False

            all_partner_ids = partner_ids + child_ids
            if company_partner_id:
                all_partner_ids.append(company_partner_id)

            record.partner_domain_ids = self.env['res.partner'].browse(all_partner_ids)