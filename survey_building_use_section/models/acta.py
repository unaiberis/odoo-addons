from odoo import fields, models


class Acta(models.Model):
    _name = "acta"
    _description = "Inspection Acta"

    inspected_building_id = fields.Many2one(
        "res.partner", required=True, string="Building"
    )
    acta_number = fields.Char()
    inspection_start_date = fields.Date()
    inspection_end_date = fields.Date()
    inspection_type = fields.Selection(
        [
            ("periodic", "Periodic"),
            ("volunteer", "Volunteer"),
            ("correction_of_deficiencies", "Correction of Deficiencies"),
        ],
    )
    inspector_id = fields.Many2one("res.partner", string="Inspector")
