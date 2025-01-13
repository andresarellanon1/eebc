from odoo import fields, models, api

class ResCompany(models.Model):

    _inherit = 'res.company'

    branch_ids = fields.One2many('res.branch', 'company_id', string="Bran")

    @api.model
    def create(self, vals):
        company = super(ResCompany, self).create(vals)
        
        self.env['res.branch'].create({
            'name': company.name,
            'company_id': company.id,
        })
        return company