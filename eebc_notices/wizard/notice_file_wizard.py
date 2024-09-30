# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

import base64
import pandas as pd
import io

import logging

_logger = logging.getLogger(__name__)

# TODO: 
#  Dejar de buscar en todas las hojas del excel - LISTO!!
#  Crear ventanas emergentes para validacion en caso de que la cantidad del excel sea mayor a la de la orden de compra, es decir que la cantidad de orden de compra debe ser menor o igual al del excel
# Agregar a la vista del wizard la cantidad de la linea de la orden de compra y la cantidad que esta en el excel del respectivo producto al cual se le desea crear aviso.
# No permitir de momento que se registren nuevos productos con el mismo numero de folio en caso de haber sido registrado previamente. (colocar ventana emergente que mencione el error)

class NoticeFileWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "notice.file.wizard"
    _description = "Wizard to recover data from xlsx file"

    file_xlsx = fields.Binary(string="Archivo" )
    file_name = fields.Char(string="Nombre del archivo")  # Campo para almacenar el nombre del archivo

   
    quantity = fields.Float(string="Cantidad", 
    readonly=True 
    )

    def action_data_analysis(self):
        _logger.warning('producto: %s', self._context['product_id'])
        self.quantity = self._context['cantidad']
        id_producto = self._context['product_id']
        supplier = self._context['proveedor']
        origin = self._context['origin']
        type_picking = self._context['type']
        location_id = self._context['location_id']
        location_dest_id = self._context['location_dest_id']
        
        if not self.file_xlsx:
            raise ValueError("Por favor, sube un archivo.")
        
        if not self.file_name:
            raise ValueError("El archivo no tiene un nombre válido.")

        # Decodificar el archivo binario (base64) a contenido binario
        file_content = base64.b64decode(self.file_xlsx)

        # Crear un objeto BytesIO a partir del contenido decodificado
        file_stream = io.BytesIO(file_content)

        # Verificar la extensión del archivo usando file_name
        if self.file_name.endswith('.csv'):
            raise ValueError("Este método solo procesa archivos XLSX. Por favor, sube un archivo Excel.")
        elif self.file_name.endswith('.xlsx'):
            # Leer solo la primera hoja del archivo Excel
            df = pd.read_excel(file_stream, sheet_name=0)  # Carga solo la primera hoja como DataFrame
        else:
            raise ValueError("Formato de archivo no soportado. Solo se permiten archivos Excel.")

        notice_data = []

        _logger.info(f"Procesando la primera hoja del archivo Excel.")

        # Verificar si la columna 'Recurso' existe en la primera hoja
        if 'Recurso' not in df.columns:
            _logger.warning("La columna 'Recurso' no existe en la primera hoja.")
            return {'type': 'ir.actions.act_window_close'}

        # Buscar el valor del producto en la columna 'Recurso'
        matching_rows = df[df['Recurso'] == id_producto]

        if not matching_rows.empty:
            _logger.info(f"Se encontraron filas que coinciden con el producto {id_producto}:")
            _logger.info(matching_rows)
            
            
            archivo_quantity = row.get('Cantidad', 0)

            # Extraer la información que necesitamos de las filas coincidentes
            for index, row in matching_rows.iterrows():
                notice_data.append({
                    'resource': row.get('Recurso', 0),  # notices.notices
                    'quantity': row.get('Cantidad', 0),  # notices.notices
                    'description': row.get('Cantidad', 0),  # notices.notices
                    'supplier': supplier,  # notices.notices
                    'notice': row.get('Aviso', 0),  # notices.notices
                    'location_id': location_id,  # notices.history
                    'location_dest': location_dest_id,  # notices.history
                    'picking_code': type_picking,  # notices.history
                    'origin': origin,  # notices.history
                })


                if archivo_quantity != self.quantity:
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'target': 'new',
                        'name': 'Cantidad incorrecta',
                        'context': {
                            'default_message': f"La cantidad en el archivo ({archivo_quantity}) no coincide con la cantidad esperada ({self.quantity}).",
                        }
                    }
        else:
            _logger.info(f"No se encontraron coincidencias para el producto {id_producto} en la primera hoja.")

        # Llamar a _create_notice si se encontraron datos
        if notice_data:
            self._create_notice(notice_data)

        return {'type': 'ir.actions.act_window_close'}

    def _create_notice(self, notice_data):
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo"""
        for data in notice_data:
            _logger.info(f"Creando aviso para el producto {data['resource']} con cantidad {data['quantity']}")
            its_created = self.env['notices.notices'].search([('notice','=', data['notice'])])
            _logger.warning('VALOR DE ITS CREATED : %s', its_created)


            if its_created:

                its_created.write({
                'history_ids': [(0, 0, {
                    'location_dest': data['location_dest'],  # Añade los campos necesarios para history
                    'location_id': data['location_id'],
                    'quantity': data['quantity'],
                    'picking_code': data['picking_code'],
                    })]
                })

                _logger.info('Historial actualizado correctamente para el aviso.')
            else:
                # Crear el nuevo registro en el modelo 'notices.notices'
                notice = self.env['notices.notices'].create({
                    'resource': data['resource'],  # ID del producto
                    'quantity': data['quantity'],  # Cantidad extraída del archivo
                    'description': data['description'],
                    'supplier': data['supplier'],
                    'notice': data['notice'],
                    
                    
                })

                self.env['notices.history'].create({
                    'location_id': data['location_id'], 
                    'location_dest': data['location_dest'], 
                    'quantity': data['quantity'],  # Cantidad extraída del archivo
                    'picking_code': data['picking_code'],
                    'notice_id':notice.id,
                    
                    
                })



        _logger.info(f"{len(notice_data)} avisos creados correctamente.")

        
        
    def _create_history_notice(self, notice_history_data):
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo"""
        for data in notice_history_data:
            _logger.info(f"Creando aviso para el producto {data['product_id']} con cantidad {data['quantity']}")
            
            # Crear el nuevo registro en el modelo 'notices.notices'
            self.env['notices.history'].create({
                'resource': data['product_id'],  # ID del producto
                'quantity': data['quantity'],  # Cantidad extraída del archivo
                'description': data['description'],
                'file_name': data['file_name'],
            })

        _logger.info(f"{len(notice_history_data)} avisos creados correctamente.")
        
        



        # Ya conseguimos la informacion del excel 
        # Ahora debemos de crear un metodo para que cree una entra
        # _logger.warning('Entramos a action_data_analysis')
        # _logger.warning(f"Nombre del archivo: {self.file_xlsx}")
        # _logger.warning(f"Nombre del wizard: {self.name}")
        # _logger.warning(f"Cantidad: {self.quantity}")







