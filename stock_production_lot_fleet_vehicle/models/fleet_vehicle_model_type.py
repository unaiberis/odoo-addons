# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class FleetVehicleModelType(models.Model):
    _name = "fleet.vehicle.model.type"
    _description = "Vehicle type"

    name = fields.Char(string="Type")
