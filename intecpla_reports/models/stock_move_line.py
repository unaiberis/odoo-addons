# Copyright 2024 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        out_picking_lines = self.filtered(lambda x: x.picking_code == "outgoing")
        in_picking_lines = self.filtered(lambda x: x.picking_code == "incoming")
        for aggregated_move_line in aggregated_move_lines:
            aggregated_move_lines[aggregated_move_line]["code"] = ""
            aggregated_move_lines[aggregated_move_line]["description"] = ""
            product = aggregated_move_lines[aggregated_move_line]["product"]
            if out_picking_lines:
                if product.alternative_sales_code:
                    aggregated_move_lines[aggregated_move_line][
                        "code"
                    ] = product.alternative_sales_code
                if not product.alternative_sales_code and product.default_code:
                    aggregated_move_lines[aggregated_move_line][
                        "code"
                    ] = product.default_code
                if product.name2:
                    aggregated_move_lines[aggregated_move_line]["name"] = product.name2
                else:
                    aggregated_move_lines[aggregated_move_line]["name"] = product.name
            if in_picking_lines:
                aggregated_move_lines[aggregated_move_line][
                    "description"
                ] = product.sudo().description_pickingin
        return aggregated_move_lines
