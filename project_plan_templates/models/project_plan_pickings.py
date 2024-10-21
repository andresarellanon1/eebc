from odoo import fields, models, api

class ProjectPlanPickings(models.Model):

    _name = 'project.plan.pickings'
    _description = 'Project plan pickings'

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    creation_date = fields.Date(string="Created on", default=fields.Date.context_today, readonly=True)
    creator_id = fields.Many2one('res.users', string="Created by", default=lambda self: self.env.user)

    