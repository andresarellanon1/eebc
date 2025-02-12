from odoo import fields, models, api

class ProjectPickingWizardLine(models.TransientModel):
    _name = 'project.picking.wizard.line'
    _description = 'Porject picking wizard lines'
    _order = 'sequence'

    name = fields.Char(string="Name")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity")
    location_id = fields.Many2one('stock.location', string="Location")
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    reservado = fields.Float(string='Reservado')
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    standard_price = fields.Float(string="Price", compute='_compute_standard_price')
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    total_cost = fields.Float(string="Total cost")

    display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    code = fields.Char(string="Code")
    sequence = fields.Integer()

    product_packaging_id = fields.Many2one('product.packaging', string="Empaquetado", domain="[('product_id', '=', product_id)]", check_company=True)
    product_uom = fields.Many2one('uom.uom', string='Unidad de medida')
    company_id = fields.Many2one('res.company', string="Empresa")
    product_uom_qty = fields.Float(string="Demanda")
    for_modification = fields.Boolean()
    for_newlines = fields.Boolean()

    wizard_creation_id = fields.Many2one(
        'project.creation.wizard',  # Modelo relacionado
        string="Wizard Creation",  # Etiqueta del campo
        ondelete='cascade'  # Eliminar líneas si se elimina el wizard
    )

    @api.depends('product_id')
    def _compute_standard_price(self):
        """
        Calcula el precio estándar del producto basado en el campo 'standard_price' del producto seleccionado.
        Este método se ejecuta automáticamente cuando cambia el campo 'product_id'.
        """
        for record in self:
            # Asignar el precio estándar del producto al campo 'standard_price' del registro actual
            record.standard_price = record.product_id.standard_price


    @api.depends('quantity')
    def _compute_subtotal(self):
        """
        Calcula el subtotal multiplicando el precio estándar por la cantidad.
        Este método se ejecuta automáticamente cuando cambia el campo 'quantity'.
        Si la cantidad es negativa, el subtotal se establece en 0.00.
        """
        for record in self:
            quantity = record.quantity

            # Verificar si la cantidad es válida (no negativa)
            if quantity >= 0:
                # Calcular el subtotal multiplicando el precio estándar por la cantidad
                record.subtotal = record.standard_price * quantity
            else:
                # Si la cantidad es negativa, establecer el subtotal en 0.00
                record.subtotal = 0.00