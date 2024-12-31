from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2one('res.branch', string='Branch', store=True,
        help='Leave this field empty if this product is shared between all branches'
    )

    allowed_branch_ids = fields.Many2one('res.branch', store=True,
        string='Allowed branches',
        compute='_compute_allowed_branch_ids'
    )

    @api.depends('company_id')
    def _compute_allowed_branch_ids(self):
        for po in self:
            po.allowed_branch_ids = self.env.user.branch_ids.ids