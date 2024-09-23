# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

import base64
import pandas as pd
import io

import logging

_logger = logging.getLogger(__name__)
class NoticeFileWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "notice.file.wizard"
    _description = "Wizard to recover data from xlsx file"

    file_xlsx = fields.Binary(string="Archivo" )
    file_name = fields.Char(string="Nombre del archivo")  # Campo para almacenar el nombre del archivo

   
    quantity = fields.Float(string="Cantidad")
    
    def action_data_analysis(self):
        _logger.warning('producto: %s', self._context['product_id'])
        id_producto = self._context['product_id']
        
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
            # Leer todas las hojas del archivo en un diccionario
            sheets = pd.read_excel(file_stream, sheet_name=None)  # Devuelve un diccionario con DataFrames
        else:
            raise ValueError("Formato de archivo no soportado. Solo se permiten archivos Excel.")

        # Iterar sobre todas las hojas del archivo
        for sheet_name, df in sheets.items():
            _logger.info(f"Procesando la hoja: {sheet_name}")

            # Verificar si la columna 'Recurso' existe en la hoja
            if 'Recurso' not in df.columns:
                _logger.warning(f"La columna 'Recurso' no existe en la hoja {sheet_name}.")
                continue  # Pasar a la siguiente hoja si la columna no existe

            # Buscar el valor del producto en la columna 'Recurso'
            matching_rows = df[df['Recurso'] == id_producto]

            if not matching_rows.empty:
                _logger.info(f"Se encontraron filas que coinciden con el producto {id_producto} en la hoja {sheet_name}:")
                _logger.info(matching_rows)
                # Aquí puedes realizar alguna acción con las filas encontradas
            else:
                _logger.info(f"No se encontraron coincidencias para el producto {id_producto} en la hoja {sheet_name}.")

        return {'type': 'ir.actions.act_window_close'}
        # _logger.warning('Entramos a action_data_analysis')
        # _logger.warning(f"Nombre del archivo: {self.file_xlsx}")
        # _logger.warning(f"Nombre del wizard: {self.name}")
        # _logger.warning(f"Cantidad: {self.quantity}")







