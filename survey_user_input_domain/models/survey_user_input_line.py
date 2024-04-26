from odoo import models, fields, api

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    calculated_matrix_question_id = fields.Many2one(
        'survey.question.answer', 
        string='Matrix Question ID',
        compute='_compute_matrix_question_id',
        store=True 
    )
    
    calculated_suggested_answer_question_id = fields.Many2one(
        'survey.question.answer', 
        string='Suggested Answer ID',
        compute='_compute_suggested_answer_id',
        store=True 
    )


    @api.depends('matrix_row_id')
    def _compute_matrix_question_id(self):
        for line in self:
            if line.matrix_row_id:
                line.calculated_matrix_question_id = line.matrix_row_id.matrix_question_id.id
            else:
                line.calculated_matrix_question_id = False


    @api.depends('suggested_answer_id')
    def _compute_suggested_answer_id(self):
        for line in self:
            if line.question_id:
                line.calculated_suggested_answer_question_id = line.suggested_answer_id.question_id.id
            else:
                line.calculated_suggested_answer_question_id = False
