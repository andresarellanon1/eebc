from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    sem = fields.Integer (string="Sem", compute='_compute_sem')

    def _compute_sem(self):
        for record in self:
            if record.date_planned and record.create_date:
                # Convertir las fechas a datetime
                fecha_creacion = fields.Datetime.from_string(record.create_date)
                fecha_entrega = fields.Datetime.from_string(record.date_planned)

                # Calcular la diferencia en semanas
                diferencia = (fecha_entrega - fecha_creacion).days
                record.sem = diferencia // 7  # División entera para obtener semanas
                if record.sem == -1:
                    record.sem = 0
            else:
                record.sem = 0

    def _get_name_purchase_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'

    