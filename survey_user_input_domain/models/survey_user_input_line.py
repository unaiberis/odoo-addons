import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

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

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

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

    def init(self):
        _logger.info("Initializing SurveyUserInputLine model")
        self._compute_matrix_question_id()
        self._compute_suggested_answer_id()

    @api.depends('matrix_row_id')
    def _compute_matrix_question_id(self):
        for line in self:
            if line.matrix_row_id:
                new_value = line.matrix_row_id.matrix_question_id.id
                if line.calculated_matrix_question_id != new_value:
                    _logger.info(f"Changing calculated_matrix_question_id for line {line.id} to {new_value}")
                    line.calculated_matrix_question_id = new_value
            else:
                if line.calculated_matrix_question_id:
                    _logger.info(f"Resetting calculated_matrix_question_id for line {line.id} to False")
                line.calculated_matrix_question_id = False

    @api.depends('suggested_answer_id')
    def _compute_suggested_answer_id(self):
        for line in self:
            if line.question_id:
                new_value = line.suggested_answer_id.question_id.id
                if line.calculated_suggested_answer_question_id != new_value:
                    _logger.info(f"Changing calculated_suggested_answer_question_id for line {line.id} to {new_value}")
                    line.calculated_suggested_answer_question_id = new_value
            else:
                if line.calculated_suggested_answer_question_id:
                    _logger.info(f"Resetting calculated_suggested_answer_question_id for line {line.id} to False")
                line.calculated_suggested_answer_question_id = False
