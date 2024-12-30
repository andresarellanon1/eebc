from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_generate_report(self):
        # Aquí obtenemos los datos de la orden de venta
        self.ensure_one()  # Aseguramos que solo se trabaje con una sola orden

        # Llamamos al reporte que se generará (definido más adelante)
        report = self.env.ref('project_plan_templates.report_analytics')  # Reemplaza con tu reporte real
        return report.report_action(self)
