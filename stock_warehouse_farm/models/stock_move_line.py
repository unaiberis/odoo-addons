# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_id = fields.Many2one(
        string="Picking Section",
        comodel_name="stock.picking.type",
        related="picking_id.picking_type_id",
        store=True,
    )
    category_type_id = fields.Many2one(
        string="Origin Section",
        comodel_name="category.type",
        related="picking_id.picking_type_id.category_type_id",
        store=True,
    )
    dest_category_type_id = fields.Many2one(
        string="Destination Section",
        comodel_name="category.type",
        related="picking_id.picking_type_id.dest_category_type_id",
        store=True,
    )
    product_family_id = fields.Many2one(
        string="Family",
        comodel_name="product.family",
        related="product_id.product_family_id",
        store=True,
    )
