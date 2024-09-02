from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class MailCompose(models.TransientModel):
    _name = 'mail.compose.message'
    _inherit = 'mail.compose.message'
    _description = "Sale Send"

    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        string="Sales",
        compute='_compute_sale_ids',
        store=True,
    )

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Recipients",
        readonly=False,
    )

    partner_sale_domain_ids = fields.One2many(
        comodel_name='res.partner',
        compute='_compute_partner_domain_ids',
        store=False,
    )

    @api.depends('partner_ids')
    def _compute_sale_ids(self):
        for record in self:
            sales = self.env['sale.order'].search([('partner_id', 'in', record.partner_ids.ids)])
            record.sale_ids = sales
            logger.warning(f"Computed sales: {sales}")

    @api.depends('sale_ids', 'record_company_id')
    def _compute_partner_domain_ids(self):
        for record in self:
            partner_ids = record.sale_ids.mapped('partner_id.id')
            logger.warning(f"Padres: {partner_ids}")
            child_ids = record.sale_ids.mapped('partner_id.child_ids.id')
            logger.warning(f"Hijos: {child_ids}")
            company_partner_id = record.record_company_id.partner_id.id if record.record_company_id and record.record_company_id.partner_id else False

            all_partner_ids = partner_ids + child_ids
            if company_partner_id:
                all_partner_ids.append(company_partner_id)
            record.partner_sale_domain_ids = self.env['res.partner'].browse(all_partner_ids)