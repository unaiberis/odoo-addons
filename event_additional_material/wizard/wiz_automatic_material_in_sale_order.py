# Copyright 2021 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizAutomaticMaterialInSaleOrder(models.TransientModel):
    _name = "wiz.automatic.material.in.sale.order"
    _description = "Wizard for put additinal material in sale order."

    name = fields.Text(string="Description")

    def action_put_material_from_registration(self):
        self.ensure_one()
        registrations = self.env["event.registration"].browse(
            self.env.context.get("active_ids")
        )
        registrations.put_in_sale_order_additional_material()
