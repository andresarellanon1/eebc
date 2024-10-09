from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    sem = fields.Integer (string="Sem", compute='_compute_sem')

    def _compute_sem(self):
        for record in self:
            if record.date_planned and record.date_approve:
                # Convertir las fechas a datetime
                fecha_aprovacion = fields.Datetime.from_string(record.date_approve)
                fecha_entrega = fields.Datetime.from_string(record.date_planned)

                # Calcular la diferencia en semanas
                diferencia = (fecha_entrega - fecha_aprovacion).days
                record.sem = diferencia // 7  # División entera para obtener semanas
            else:
                record.sem = 0

    def _get_name_purchase_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'

    