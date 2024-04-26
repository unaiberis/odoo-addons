import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    calculated_matrix_question_id = fields.Many2Many(
        'survey.question.answer', 
        string='Matrix Question ID',
        compute='_compute_matrix_question_id',
        store=True 
    )
    
    calculated_suggested_answer_question_id = fields.Many2Many(
        'survey.question.answer', 
        string='Suggested Answer ID',
        compute='_compute_suggested_answer_id',
        store=True 
    )

    def initialize_survey_user_input_line(self):
        _logger.info("2024okdeb - Initializing SurveyUserInputLine model")
        self._compute_matrix_question_id()
        self._compute_suggested_answer_id()

    @api.depends('matrix_row_id')
    def _compute_matrix_question_id(self):
        for line in self:
            if line.matrix_row_id:
                new_value = line.matrix_row_id.matrix_question_id.id
                if line.calculated_matrix_question_id != new_value:
                    _logger.info(f"2024okdeb - Changing calculated_matrix_question_id for line {line.id} to {new_value}")
                    line.calculated_matrix_question_id = new_value
            else:
                self._reset_calculated_matrix_question_id(line)

    def _reset_calculated_matrix_question_id(self, line):
        if line.calculated_matrix_question_id:
            _logger.info(f"2024okdeb - Resetting calculated_matrix_question_id for line {line.id} to False")
        line.calculated_matrix_question_id = False

    @api.depends('suggested_answer_id')
    def _compute_suggested_answer_id(self):
        for line in self:
            if line.question_id:
                new_value = line.suggested_answer_id.question_id.id
                if line.calculated_suggested_answer_question_id != new_value:
                    _logger.info(f"2024okdeb - Changing calculated_suggested_answer_question_id for line {line.id} to {new_value}")
                    line.calculated_suggested_answer_question_id = new_value
            else:
                self._reset_calculated_suggested_answer_question_id(line)

    def _reset_calculated_suggested_answer_question_id(self, line):
        if line.calculated_suggested_answer_question_id:
            _logger.info(f"2024okdeb - Resetting calculated_suggested_answer_question_id for line {line.id} to False")
        line.calculated_suggested_answer_question_id = False
