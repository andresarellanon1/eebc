from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    sem = fields.Integer (string="Sem", compute='_compute_sem')

    def _compute_sem(self):
        for record in self:
            if record.date_planned and record.create_date:
                # Convertir las fechas a datetime y luego a solo fecha
                fecha_creacion = fields.Datetime.from_string(record.create_date).date()
                fecha_entrega = fields.Datetime.from_string(record.date_planned).date()

                # Calcular la diferencia en días
                diferencia = (fecha_entrega - fecha_creacion).days

                # Calcular el número de semanas
                record.sem = max(0, diferencia // 7)  # Asegurarse de que no sea negativo
            else:
                record.sem = 0

    def _get_name_purchase_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'

    