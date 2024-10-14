import os
import logging
from odoo import api, SUPERUSER_ID, exceptions
from PIL import Image
import base64
import io

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    image_directory = '/home/azureuser/Fotos_Gove-Trodis'
    
    if not os.path.exists(image_directory):
        _logger.warning("El directorio no existe: %s", image_directory)
        return

    for filename in os.listdir(image_directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            default_code = os.path.splitext(filename)[0]

            product = env['product.template'].search([('default_code', '=', default_code)], limit=1)
            if product:
                try:
                    image_path = os.path.join(image_directory, filename)

                    with open(image_path, 'rb') as image_file:
                        image_data = image_file.read()
                        # Intenta decodificar la imagen para asegurar que es válida
                        img = Image.open(io.BytesIO(image_data))
                        img.verify()  # Esto lanza un error si la imagen no es válida
                        img.close()

                    # Almacena la imagen en base64
                    product.image_1920 = base64.b64encode(image_data)

                    _logger.info("Imagen actualizada para el producto: %s", default_code)
                except Exception as e:
                    _logger.error("Error al actualizar la imagen para el producto %s: %s", default_code, str(e))
                    raise exceptions.UserError(f"Error al actualizar la imagen para el producto '{default_code}'. Detalles del error: {str(e)}.")
            else:
                _logger.warning("No se encontró el producto con default_code: %s", default_code)
