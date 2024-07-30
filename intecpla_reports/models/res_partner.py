# Copyright 2020 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def get_state_name(self):
        name = ""
        if self.state_id:
            state_name = self.state_id.name
            if "(" not in state_name:
                name = "({})".format(state_name)
            else:
                parenthesis_index = state_name.find("(")
                name = "( {})".format(state_name[:parenthesis_index])
        return name
