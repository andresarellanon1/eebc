from odoo import models, fields, api



class LabsImgs(models.Model):
    _name = 'sanatorio.quiroz.labs.imgs'
    _description = 'Labs/Imgs'

    lbim_fecha = fields.Date(string="Fecha")
    lbim_tipo = fields.Selection([('solicitud', 'Solicitud'), ('resultado', 'Resultado')], string="Tipo")
    check = fields.Selection([
        ('bh', 'BH (RBC, WBC, PLT)'), ('es3', 'ES3 (Na, K, Cl)'), ('lip', 'LIP (HDL, LDL, VLDL, Chol, TG)'),
        ('card', 'CARD (CPK, TpT, TpI, PNB)'), ('qs', 'QS (Glu, Cr, BUN, Aur)'), ('es6', 'ES6 (ES3+Ca, P, Mg)'),
        ('pfh', 'PFH (AST, ALT, GGT, BT, BI, Alb, PT)'), ('coag', 'COAG (TP, INR, TTPa)'),
        ('pncrt', 'Pncrt (Amy, Lyp)'), ('thyr', 'Thyr (TSH, T3, T4)'), ('gas', 'GAS (PO2, PCO2, PH, HCO3)'),
        ('ego', 'EGO'), ('viral', 'Viral (VIH, VHB, VHC)'), ('inmuno', 'Inmuno (IgG, IgM, IgE)'), ('otros', 'Otros')
    ], string="Check")
    tipo = fields.Selection([
        ('rx', 'RX'), ('us', 'US'), ('ct', 'CT'), ('irm', 'IRM')
    ], string="Tipo")
    region_anatomica = fields.Selection([
        ('cabeza', 'Cabeza'), ('torax', 'Tórax'), ('abdomen', 'Abdomen'), ('extremidades', 'Extremidades'),
        ('columna_cervical', 'Columna Cervical'), ('columna_lumbar', 'Columna Lumbar'),
        ('hombro', 'Hombro'), ('codo', 'Codo'), ('muñeca', 'Muñeca'), ('mano', 'Mano'),
        ('cadera', 'Cadera'), ('rodilla', 'Rodilla'), ('tobillo', 'Tobillo'), ('pie', 'Pie')
    ], string="Región Anatómica")
    especificaciones = fields.Selection([
        ('ap', 'AP'), ('pa', 'PA'), ('lat', 'Lateral'), ('obl', 'Oblicua'), ('contraste', 'Contraste')
    ], string="Especificaciones")
