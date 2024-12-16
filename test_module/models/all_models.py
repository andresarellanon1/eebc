from odoo import models, fields, api

class Paciente(models.Model):
    _name = 'sanatorio.quiroz.paciente'
    _description = 'Paciente'


    nombre = fields.Char(string="Nombre")
    apellido_paterno = fields.Char(string="Apellido Paterno")
    apellido_materno = fields.Char(string="Apellido Materno")
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento")
    edad = fields.Integer(string="Edad", compute="_compute_edad", store=True)
    sexo = fields.Selection([('masculino', 'Masculino'), ('femenino', 'Femenino')], string="Sexo")
    contacto_id = fields.Many2one('res.partner', string="Contacto")
    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    historial_administrativo_id = fields.Many2one('sanatorio.quiroz.historial.administrativo', string="Historial Administrativo")

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        for record in self:
            if record.fecha_nacimiento:
                today = fields.Date.today()
                record.edad = today.year - record.fecha_nacimiento.year - ((today.month, today.day) < (record.fecha_nacimiento.month, record.fecha_nacimiento.day))

class HistorialMedico(models.Model):
    _name = 'sanatorio.quiroz.historial.medico'
    _description = 'Historial Médico'

    hx_familiar_id = fields.Many2one('sanatorio.quiroz.historial.familiar', string="HX Familiar")
    hx_personal_id = fields.Many2one('sanatorio.quiroz.historial.personal', string="HX Personal")
    hx_alergias_ids = fields.One2many('sanatorio.quiroz.historial.alergias', 'historial_medico_id', string="HX Alergias")
    hx_clinico_ids = fields.One2many('sanatorio.quiroz.historial.clinico', 'historial_medico_id', string="HX Clínico")
    hx_quirurgico_ids = fields.One2many('sanatorio.quiroz.historial.quirurgico', 'historial_medico_id', string="HX Quirúrgico")
    evolucion_ids = fields.One2many('sanatorio.quiroz.evolucion', 'historial_medico_id', string="Evolución")

class HistorialFamiliar(models.Model):
    _name = 'sanatorio.quiroz.historial.familiar'
    _description = 'Historial Familiar'

    relacion = fields.Selection([
        ('padre', 'Padre'), ('madre', 'Madre'), ('hermano', 'Hermano'), ('hermana', 'Hermana'), ('otro', 'Otro')
    ], string="Relación")
    edad_familiar = fields.Integer(string="Edad del Familiar")
    vive = fields.Selection([('si', 'Sí'), ('no', 'No')], string="¿Vive?")
    relacion_hereditaria = fields.Text(string="Relación Hereditaria")

class HistorialPersonal(models.Model):
    _name = 'sanatorio.quiroz.historial.personal'
    _description = 'Historial Personal'

    religion = fields.Selection([
        ('catolica', 'Católica'), ('protestante', 'Protestante'), ('otra', 'Otra')
    ], string="Religión")
    escolaridad = fields.Selection([
        ('primaria', 'Primaria'), ('secundaria', 'Secundaria'), ('universidad', 'Universidad')
    ], string="Escolaridad")
    ocupacion = fields.Text(string="Ocupación")
    dieta = fields.Text(string="Dieta")
    actividad_fisica = fields.Text(string="Actividad Física")
    higiene_personal = fields.Text(string="Higiene Personal")

class HistorialAlergias(models.Model):
    _name = 'sanatorio.quiroz.historial.alergias'
    _description = 'Historial Alergias'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    alergeno = fields.Selection([
        ('polen', 'Polen'), ('polvo', 'Polvo'), ('otros', 'Otros')
    ], string="Alergeno")
    rxa_anio = fields.Date(string="RXA Año")
    reaccion = fields.Text(string="Reacción")
    tratamiento = fields.Text(string="RXA Tratamiento")

class HistorialClinico(models.Model):
    _name = 'sanatorio.quiroz.historial.clinico'
    _description = 'Historial Clínico'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    intervencion = fields.Selection([('consulta', 'Consulta'), ('ingreso', 'Ingreso')], string="Intervención")
    diagnostico = fields.Char(string="Diagnóstico")
    dx_anio = fields.Date(string="DX Año")
    tratamiento_id = fields.Many2one('sanatorio.quiroz.tratamiento', string="Tratamiento")
    dx_evolucion = fields.Text(string="DX Evolución")
    dx_comentarios = fields.Text(string="DX Comentarios")

class Tratamiento(models.Model):
    _name = 'sanatorio.quiroz.tratamiento'
    _description = 'Tratamiento'

    historial_clinico_id = fields.Many2one('sanatorio.quiroz.historial.clinico', string="Historial Clínico")
    medicamento = fields.Char(string="Medicamento")
    presentacion = fields.Text(string="Presentación")
    dosis = fields.Integer(string="Dosis")
    frecuencia = fields.Float(string="Frecuencia")
    duracion = fields.Integer(string="Duración")

class HistorialQuirurgico(models.Model):
    _name = 'sanatorio.quiroz.historial.quirurgico'
    _description = 'Historial Quirúrgico'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    qx_diagnostico = fields.Char(string="QX Diagnóstico")
    qx_anio = fields.Date(string="QX Año")
    procedimiento = fields.Text(string="Procedimiento")
    qx_comentarios = fields.Text(string="QX Comentarios")

class Evolucion(models.Model):
    _name = 'sanatorio.quiroz.evolucion'
    _description = 'Evolución'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    evol_fecha = fields.Date(string="Evol Fecha")
    intervencion = fields.Selection([('consulta', 'Consulta'), ('ingreso', 'Ingreso')], string="Intervención")
    interrogatorio_id = fields.Many2one('sanatorio.quiroz.interrogatorio', string="Interrogatorio")
    motivo_ingreso = fields.Text(string="Motivo de Ingreso")
    exploracion_id = fields.Many2one('sanatorio.quiroz.exploracion', string="Exploración")
    labs_imgs_id = fields.Many2one('sanatorio.quiroz.labs.imgs', string="Labs/Imgs")
    analisis = fields.Text(string="Análisis")
    diagnostico = fields.Text(string="Diagnóstico")
    plan = fields.Text(string="Plan")
    pronostico = fields.Selection([('b', 'Bueno'), ('m', 'Malo'), ('r', 'Regular')], string="Pronóstico")
    motivo_egreso = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Motivo de Egreso")

class Interrogatorio(models.Model):
    _name = 'sanatorio.quiroz.interrogatorio'
    _description = 'Interrogatorio'

    sintoma = fields.Text(string="Síntoma")
    ss_inicio = fields.Integer(string="Inicio (días)")
    ss_localizacion = fields.Text(string="Localización")
    ss_intensidad = fields.Selection([('lo', 'Lo'), ('me', 'Me'), ('hi', 'Hi')], string="Intensidad")
    ss_irradiacion = fields.Text(string="Irradiación")
    ss_atenuantes = fields.Text(string="Atenuantes")
    ss_agravantes = fields.Text(string="Agravantes")

class Exploracion(models.Model):
    _name = 'sanatorio.quiroz.exploracion'
    _description = 'Exploración'

    signos_vitales_id = fields.Many2one('sanatorio.quiroz.signos.vitales', string="Signos Vitales")
    region_anatomica = fields.Selection([
        ('cc', 'Cabeza y Cuello'), ('tx', 'Tórax'), ('ab', 'Abdomen'), ('gn', 'Genitales'), ('br', 'Brazos'), ('lg', 'Piernas')
    ], string="Región Anatómica")
    hallazgo = fields.Text(string="Hallazgo")

class SignosVitales(models.Model):
    _name = 'sanatorio.quiroz.signos.vitales'
    _description = 'Signos Vitales'

    ta = fields.Integer(string="TA (mmHg)")
    fc = fields.Integer(string="FC (lpm)")
    fr = fields.Integer(string="FR (rpm)")
    spo2 = fields.Integer(string="SpO2 (%)")
    temp = fields.Integer(string="Temperatura (°C)")
    eva = fields.Integer(string="EVA (0-10)")
    glasgow = fields.Integer(string="GLASGOW (3-15)")
    peso = fields.Integer(string="Peso (kg)")
    talla = fields.Float(string="Talla (m)")
    imc = fields.Float(string="IMC")

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
