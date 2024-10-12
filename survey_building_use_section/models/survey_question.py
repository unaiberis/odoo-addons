# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    question_normative_ids = fields.Many2many(
        "survey.question.normative",
        string="Question Normatives",
    )
    is_normative_filter = fields.Boolean("Normative Filter")
    questions_to_filter = fields.Many2many(
        "survey.question",
        string="Questions to filter",
        relation="survey_question_filter_rel",
        column1="questions_to_filter",
        column2="normative_filter_question_id",
    )

    def update_normative_filter_answers(self):
        normative_filter_questions = self.filtered(lambda q: q.is_normative_filter)

        for normative_filter_question in normative_filter_questions:
            existing_answers = normative_filter_question.suggested_answer_ids

            normative_data = self.env["survey.question.normative"].search([])

            normative_ids = normative_data.mapped("id")

            for answer in existing_answers:
                if not answer.answer_normative_id:
                    answer.answer_normative_id = answer.sequence
                if answer.answer_normative_id not in normative_ids:
                    answer.unlink()

            for normative in normative_data:
                if not existing_answers.filtered(
                    lambda ans: ans.answer_normative_id == normative.id
                ):
                    self.env["survey.question.answer"].create(
                        {
                            "question_id": normative_filter_question.id,
                            "value": normative.name,
                            "sequence": normative.id,
                            "answer_normative_id": normative.id,
                            "notes": normative.description,
                        }
                    )
