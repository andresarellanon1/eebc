from odoo import fields, api, models
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Project template", readonly="True")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines")

    ### Crea tareas de proyecto a partir de las líneas del plan de proyecto.
    # Valida si la tarea ya existe.
    def create_project_tasks(self):
        for project in self:  
            for line in project.project_plan_lines:
                current_task_type = self.get_or_create_task_type(line.stage_id or 'Extras', project)

                if line.use_project_task:
                    # Verificar si la tarea ya existe
                    existing_task = self.env['project.task'].search([
                        ('name', '=', line.name),
                        ('project_id', '=', project.id)
                    ], limit=1)

                    if existing_task:
                        # Lanzar un UserError para notificar al usuario
                        raise UserError(f'Tarea ya existe: {line.name} en el proyecto {project.name}.')
                    
                    # Crear la nueva tarea si no existe
                    timesheet_lines = self.env['task.time.lines'].search([
                        ('task_timesheet_id', '=', line.task_timesheet_id.id)
                    ])

                    timesheet_data = [(0, 0, {
                        'name': ts_line.description,
                        'estimated_time': ts_line.estimated_time,
                    }) for ts_line in timesheet_lines]

                    self.env['project.task'].create({
                        'name': line.name,
                        'project_id': project.id,
                        'description': line.description,
                        'planned_date_begin': line.planned_date_begin,
                        'date_deadline': line.planned_date_end,
                        'user_ids': [(6, 0, line.partner_id.ids)],
                        'stage_id': current_task_type.id,
                        'timesheet_ids': timesheet_data,
                    })

    ### Busca o crea un tipo de tarea por nombre y proyecto.
    # Args: stage_id: Nombre del tipo de tarea; project: Proyecto relacionado.
    # Returns: Tipo de tarea encontrado o creado.
    def get_or_create_task_type(self, stage_id, project):
        task_type = self.env['project.task.type'].search([
            ('name', '=', stage_id),
            ('project_ids', 'in', project.id)
        ], limit=1)

        if not task_type:
            task_type = self.env['project.task.type'].create({
                'name': stage_id,
                'project_ids': [(4, project.id)],
            })
            
        return task_type