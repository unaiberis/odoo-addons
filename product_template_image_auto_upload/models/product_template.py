import os
import base64
import logging
from PIL import Image
from io import BytesIO  # Import BytesIO class explicitly

from odoo import fields, models

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def init(self):
        _logger.info("Initializing product template image update process...")
        
        # Global variable to control whether to remove existing images
        remove_existing_images = False
        
        if remove_existing_images:
            _logger.info("Removing existing images for all products...")
            # Remove images for all products
            self.env['product.template'].search([]).write({'image_1920': False})
            _logger.info("Existing images removed.")
        
        image_folder = '/tmp/imagenes_descargadas'
        for filename in os.listdir(image_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(image_folder, filename)
                image_name = os.path.splitext(filename)[0]
                _logger.info(f"Processing image: {filename}")
                product_templates = self.env['product.template'].search([('name', '=', image_name)])
                if not product_templates:
                    _logger.info(f"Product template not found for image: {filename}")
                    # If product template not found, remove everything after the last dash and try again
                    while '-' in image_name:
                        image_name = image_name.rsplit('-', 1)[0]
                        product_templates = self.env['product.template'].search(['|', '|', ('name', 'ilike', f' {image_name} '), ('name', 'ilike', f'%{image_name} '), ('name', 'ilike', f' {image_name}%')])
                        if product_templates:
                            _logger.info(f"Found matching product template for image: {filename}")
                            break
                    else:
                        _logger.warning(f"No matching product template found for image: {filename}")
                for product_template in product_templates:
                    try:
                        # Open the image
                        with Image.open(image_path) as img:
                            # Get the dimensions of the image
                            width, height = img.size
                            # Determine the smallest dimension
                            min_dimension = min(width, height)
                            # Resize the image to a square shape using the smallest dimension
                            img = img.resize((min_dimension, min_dimension))
                            # Convert image to RGB (if not already in RGB mode)
                            img = img.convert('RGB')
                            # Create a BytesIO object to hold the compressed image data
                            with BytesIO() as buffer:
                                # Save the image to the buffer with JPEG format and compression quality 90
                                img.save(buffer, format="JPEG", quality=90)
                                # Get the compressed image data from the buffer
                                compressed_image_data = buffer.getvalue()
                        # Encode the compressed image data to base64
                        encoded_image = base64.b64encode(compressed_image_data)
                        # Assign the encoded image to the product template field
                        product_template.image_1920 = encoded_image
                        _logger.info(f"Image updated for product template: {product_template.name}")
                    except Exception as e:
                        _logger.error(f"Error updating image for product template {product_template.name}: {e}")
        _logger.info("Product template image update process completed.")
