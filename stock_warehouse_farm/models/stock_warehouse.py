# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    farm_area = fields.Float()
    farm_capacity = fields.Float()
    farm_owned = fields.Boolean()
    farm_numexp = fields.Char()
    farm_maximum = fields.Float()
    farm_minimum = fields.Float()
    farm_distance = fields.Float()
    partner_latitude = fields.Float(
        related="partner_id.partner_latitude",
        store=True,
    )
    partner_longitude = fields.Float(
        related="partner_id.partner_longitude",
        store=True,
    )
