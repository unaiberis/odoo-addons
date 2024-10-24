# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class SlideSlide(models.Model):
    _inherit = "slide.slide"

    def _compute_count_statistics(self):
        for statistic in self:
            statistic.count_statistic = len(statistic.statistic_ids)

    statistic_ids = fields.One2many(
        string="Statistics", inverse_name="slide_id", comodel_name="slide.slide.partner"
    )
    count_statistic = fields.Integer(
        "# Statistics", compute="_compute_count_statistics"
    )

    def action_view_statistics(self):
        context = self.env.context.copy()
        context.update({"default_slide_id": self.id})
        return {
            "name": _("Statistics"),
            "view_mode": "tree,form",
            "res_model": "slide.slide.partner",
            "domain": [("id", "in", self.statistic_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context,
        }
