from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    HOURS = [
        ('00:00', '00:00'),
        ('01:00', '01:00'),
        ('02:00', '02:00'),
        ('03:00', '03:00'),
        ('04:00', '04:00'),
        ('05:00', '05:00'),
        ('06:00', '06:00'),
        ('07:00', '07:00'),
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
        ('20:00', '20:00'),
        ('21:00', '21:00'),
        ('22:00', '22:00'),
        ('23:00', '23:00')
    ]

    is_customer = fields.Boolean(default=False, string="Es cliente")
    is_customer_foreign = fields.Boolean(default=False, string="Es extranjero")
    is_government = fields.Boolean(default=False, string="Es del gobierno")

    commercial_name = fields.Char(string="Nombre comercial")

    customer_need_purchase_order = fields.Boolean(
        default=False,
        string="Requiere orden de compra.",
        help="Activar este campo habilita la validación de la referencia de orden de compra del cliente en los documentos de venta.")

    customer_sales_person_name = fields.Char(
        string="Contacto de ventas.",
        help="Nombre del contacto de atención a ventas.")
    customer_billing_person_name = fields.Char(
        string="Contacto de cobranza.",
        help="Nombre del contacto de cobranza.")
    customer_sales_person_email = fields.Char(
        string="Correo de ventas.",
        help="Correo del contacto de atención a ventas. Se usa para el envío de facturas.")
    customer_billing_person_email = fields.Char(
        string="Correo de cobranza.",
        help="Correo del contacto de cobranza. Se usa para el envío de complementos de pago.")
    customer_foreign_email = fields.Char(
        string="Correo extranjero.",
        help="Se usa para avisos de clientes extranjeros.")

    customer_down_motive = fields.Char(string="Motivo de baja.")

    customer_receipt_invoice_conditions = fields.Char(
        string="Condiciones de recepción de facturas.")
    customer_payment_invoice_conditions = fields.Char(
        string="Condiciones de pago de facturas.")

    customer_bday = fields.Date(string="Cumpleaños del cliente.")

    customer_number_reference = fields.Char(string="Referencia del cliente.")

    orders_residual = fields.Monetary(string='Ordenes por facturar', compute='orders_amount_residual')

    invoice_residual = fields.Monetary(string='Facturas por cobrar', compute='invoice_residual_amount')

    total_residual = fields.Monetary(string='Total por cobrar', compute='_compute_total')

    customer_credit_suspend = fields.Boolean(
        default=False,
        string="Crédito suspendido.",
    )

    customer_manual_suspend = fields.Boolean(
        default=False,
        string="Crédito suspendido manual"
    )

    customer_credit_key = fields.Boolean(
        default=False,
        string="Llave de crédito.",
        help="Abrir la llave de crédito.")

    customer_counter_receipt = fields.Boolean(
        default=False,
        string="Contrarecibo.",
        help="Si el cliente necesita o no contrarecibo.")

    customer_credit_days = fields.Integer(string='Días de crédito.', help='')
    customer_tax = fields.Integer(string='IVA del cliente.', help='Se calcula por encima del IVA del producto.')
    customer_tax_retention = fields.Integer(string='Retención del IVA.', help="Se calcula automáticamente sí está activo.")
    customer_tax_isr_retention = fields.Integer(string='Retención del ISR.', help="Se calcula automáticamente sí está activo.")

    customer_cond_payment = fields.Selection(
        [
            ("PUE", "PUE"),
            ("PPD", "PPD"),
        ],
        string="CondPago"
    )

    customer_counter_receipt_type = fields.Selection(
        [
            ("P", "Físico"),
            ("E", "Electrónico"),
        ],
        string="Tipo de contrarecibo"
    )

    # HORARIOS #
    customer_counter_receipt_days = fields.Many2many(
        'res.weekday',
        string='Entrega de contrarecibo.',
        help='Días en que se entrega contrarecibo.',
        relation='customer_counter_receipt_weekdays_rel')
    customer_counter_receipt_time_frame_start = fields.Selection(
        selection=HOURS,
        string='Inicio contrarecibo.',
        help='Horario en que se entrega contrarecibo.')
    customer_counter_receipt_time_frame_end = fields.Selection(
        selection=HOURS,
        string='Fin contrarecibo.',
        help='Horario en que se entrega contrarecibo.')

    customer_payment_days = fields.Many2many(
        'res.weekday',
        string="Días pago.",
        help="Qué día programa pagos.",
        relation='customer_payment_weekdays_rel')
    customer_payment_time_frame_start = fields.Selection(
        selection=HOURS,
        string="Inicio pagos.",
        help="Inicio del horario en qué realiza pagos.")
    customer_payment_time_frame_end = fields.Selection(
        selection=HOURS,
        string="Fin pagos.",
        help="Fin del horario en que realiza pagos.")

    can_see_accoounting = fields.Boolean('Can see accounting', compute="_can_see_accoounting", store=False)

    def _can_see_accoounting(self):
        if self.env.user.has_group("morvil_security.group_morvil_sale_user") or self.env.user.has_group("morvil_security.group_morvil_purchase_user"):
            self.can_see_accoounting = False
        else:
            self.can_see_accoounting = True

    def orders_amount_residual(self):
        for partner in self:
            total = 0.0
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),  # cliente
                ('state', '=', 'sale'),  # ordenes confirmadas
                ('invoice_status', '=', 'to invoice')  # por facturar
            ])
            for order in orders:
                total += order.amount_total
            partner.orders_residual = total

    @api.onchange('parent_id')
    def _compute_commercial_name_parent_commercial_name(self):
        for partner in self:
            if partner.parent_id:
                partner.commercial_name = partner.parent_id.commercial_name

    @api.onchange('parent_id', 'customer_number_reference', 'parent_id.customer_number_reference')
    def _compute_parent_customer_number_reference(self):
        for partner in self:
            if partner.parent_id:
                partner.customer_number_reference = partner.parent_id.customer_number_reference
            elif (not partner.parent_id):
                # aquí se debería establecer la referencia de cliente actualizada para los hijos
                # TODO: Averiguar si queremos o no queremos hacer eso... creo que si
                continue

    @api.constrains('customer_counter_receipt_time_frame_start', 'customer_counter_receipt_time_frame_end')
    def _check_hours_counter_receipt(self):
        for record in self:
            if record.customer_counter_receipt_time_frame_start and record.customer_counter_receipt_time_frame_end:
                if record.customer_counter_receipt_time_frame_start >= record.customer_counter_receipt_time_frame_end:
                    raise ValidationError("La hora de inicio debe ser menor que la hora de término.")

    @api.constrains('customer_counter_receipt_time_frame_start', 'customer_counter_receipt_time_frame_end')
    def _check_hours_payment(self):
        for record in self:
            if record.customer_payment_time_frame_start and record.customer_payment_time_frame_end:
                if record.customer_payment_time_frame_start >= record.customer_payment_time_frame_end:
                    raise ValidationError("La hora de inicio debe ser menor que la hora de término.")

    def _check_credit_limit(self, amount):
        for record in self:
            # logger.warning('---------------------------------')
            # logger.warning(f'Credito limite {record.credit_limit}')
            credit = record.credit + amount
            # logger.warning(f'Credito {credit}')
            if not record.customer_manual_suspend and (credit >= record.credit_limit):
                print("credito suspendido")
                # logger.warning(f'Entra al if, suspendiendo crédito. Suspendido previamente: {record.customer_credit_suspend}')
                # record.write({'customer_credit_suspend': True})

    def invoice_residual_amount(self):
        for partner in self:
            credit = partner.credit
            partner.invoice_residual = credit

    @api.depends("orders_residual", "invoice_residual")
    def _compute_total(self):
        for record in self:
            record.total_residual = record.orders_residual + record.invoice_residual
