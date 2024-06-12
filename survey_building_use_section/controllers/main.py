# Copyright 2024 Unai Beristain, Ana Juaristi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey

_logger = logging.getLogger(__name__)

class Survey(Survey):
    @http.route()
    def survey_display_page(self, survey_token, answer_token, **post):
        res = super().survey_display_page(survey_token, answer_token, **post)

        self._create_and_fill_normative_filters(res.qcontext['survey'], res.qcontext['answer'])
 
        return request.render('survey.survey_page_fill',
            self._prepare_survey_data(res.qcontext['survey'], res.qcontext['answer'], **post))


    def _create_and_fill_normative_filters(self, current_survey_id, current_user_input_id):
        
        triggering_question_ids = request.env['survey.question'].search([('survey_id', '=', current_survey_id.id), ('is_normative_filter', '=', True)])

        for triggering_question_id in triggering_question_ids:
            if triggering_question_id.questions_to_filter:
                for question in current_survey_id.question_and_page_ids:
                    if question in triggering_question_id.questions_to_filter:
                        for triggering_question_to_filter in triggering_question_id.questions_to_filter:
                            triggered_question = triggering_question_to_filter
                            
                            triggering_question_before = triggering_question_to_filter.triggering_question_id
                            
                            # If a question has a triggering_question_id, dont change it to be activated with the normative filter
                            # Only change the first question that needs no activation, and filter it regarding normative
                            if not triggering_question_before or triggering_question_before: # and not triggering_question_before.is_normative_filter:
                                # If a question has no normative, show it no matter the normative and
                                # remove the is conditional filter
                                
                                if not triggered_question.question_normative_ids:
                                    triggered_question.write({
                                        'is_conditional': False,
                                    })
                                    
                                else:
                                    if triggered_question.question_normative_ids:
                                        # All other questions must be conditional. If they are not conditional they will be displayed 
                                        # no matter the condition
                                        triggered_question.write({
                                            'is_conditional': True,
                                            'triggering_question_id': triggering_question_id.id,
                                            'triggering_answer_id': False,
                                        })

                                        if any(normative.start_date <= current_user_input_id.inspected_building_id.service_start_date < normative.end_date
                                            for normative in question.question_normative_ids):
                                            matched_normatives = [normative for normative in question.question_normative_ids if normative.start_date <= current_user_input_id.inspected_building_id.service_start_date < normative.end_date]
                                            matching_normative_names = [normative.name for normative in matched_normatives]
                                            matched_answers = [ans for ans in triggering_question_id.suggested_answer_ids if ans.value in matching_normative_names]
                                            if matched_answers:
                                                triggering_answer = next((ans for ans in triggering_question_id.suggested_answer_ids if ans.value == matched_answers[0].value), False)
                                                if triggering_answer:
                                                    triggered_question.write({
                                                        'triggering_answer_id': triggering_answer.id,
                                                    })
                                    
                    # Write a value in triggering_answer_id not to be null
                    # Get the first normative of the question. This answer will not trigger the question 
                    # so it does not matter if it is the first or the last
                    triggering_answer = next((ans for ans in triggering_question_id.suggested_answer_ids if ans.value in [normative.name for normative in question.question_normative_ids]), False)
                    if not question.triggering_answer_id and triggering_answer and question.is_conditional:
                        question.write({
                            'triggering_answer_id': triggering_answer.id,
                        })
            
            
            self._create_automatic_user_input_lines_for_normative_questions(current_survey_id, current_user_input_id, triggering_question_id)



    def _create_automatic_user_input_lines_for_normative_questions(self, current_survey_id, current_user_input_id, triggering_question_id):
            # Create automatic responses of the normative filter question (1st question),
            # Generate the responses of the first question that is activated when pressing
            # "Add Normative Filter"

            # Select answers based on the given logic
            selected_answers = []

            # Get all normatives from the survey.question.normative table
            all_normatives = request.env['survey.question.normative'].search([])

            for answer in triggering_question_id.suggested_answer_ids:
                for normative in all_normatives:
                    # Check if any of the normatives meet the condition
                    if (normative.start_date <= current_user_input_id.inspected_building_id.service_start_date < normative.end_date
                        and answer not in selected_answers 
                        and answer.value == normative.name):

                        # Check if a record already exists for these conditions
                        existing_user_input_line = request.env['survey.user_input.line'].search([
                            ('survey_id', '=', current_survey_id.id),
                            ('question_id', '=', triggering_question_id.id),
                            ('answer_type', '=', 'suggestion'),
                            ('suggested_answer_id', '=', answer.id),
                            ('user_input_id', '=', current_user_input_id.id)
                        ])

                        if not existing_user_input_line:
                            request.env['survey.user_input.line'].create({
                                'survey_id': current_survey_id.id,
                                'question_id': triggering_question_id.id,
                                'answer_type': 'suggestion',
                                'suggested_answer_id': answer.id,
                                'user_input_id': current_user_input_id.id
                            })

                        # Dont compare this questions again because they are already selected
                        selected_answers.append(answer)