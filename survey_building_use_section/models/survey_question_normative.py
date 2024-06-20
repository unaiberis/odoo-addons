# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SurveyQuestionNormative(models.Model):
    _name = "survey.question.normative"
    _description = "Survey Question Normative"

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    error_text = fields.Text()
    start_date = fields.Date(
        required=True,
    )
    end_date = fields.Date(
        required=True,
    )
    related_article_ids = fields.One2many(
        "survey.question.article", "question_normative_id", "Related Articles"
    )
