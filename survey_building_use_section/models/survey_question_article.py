# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SurveyQuestionArticle(models.Model):
    _name = "survey.question.article"
    _description = "Survey Question Article"

    name = fields.Char(required=True)
    description = fields.Char()
    error_text = fields.Text()
    question_normative_id = fields.Many2one(
        comodel_name="survey.question.normative",
        string="Normative",
    )