# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BuildingSection(models.Model):
    _name = "building.section"
    _description = "Building Section/Area"

    name = fields.Char(
        "Description",
        required=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Contact",
        required=True,
        copy=False,
    )
    section_use = fields.Many2one(
        "building.use",
    )
    risk = fields.Char(
        copy=False,
    )
    area = fields.Float(
        "Surface",
        default=0.0,
        copy=False,
    )
    evacuation_height = fields.Float()
    configuration = fields.Selection(
        [
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
            ("E", "E"),
        ],
    )
