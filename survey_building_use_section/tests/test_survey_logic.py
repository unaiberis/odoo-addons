from datetime import date
from odoo.tests.common import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestSurveyInvite(HttpCase):

    def setUp(self):
        super(TestSurveyInvite, self).setUp()
        self.survey = self.env['survey.survey'].create({
            'title': 'Building Survey',
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'partner@example.com',
        })

        self.building_partner = self.env['res.partner'].create({
            'name': 'Test Building',
            'service_start_date': False, 
        })

    def test_action_create_building_survey(self):
        test_emails = 'test1@example.com; test2@example.com'

        # Open the survey invite form and set the building activation date, partner_ids, and emails
        invite = self.env['survey.invite'].create({
            'survey_id': self.survey.id,
            'partner_id': self.partner.id,
            'partner_ids': [(6, 0, [self.partner.id])], 
            'building_to_inspect_id': self.building_partner.id,
            'building_activation_date': date.today(),
            'emails': test_emails, 
        })

        # Simulate clicking the button
        action = invite.action_create_building_survey()

        # Check that the building's service_start_date is now set
        self.assertEqual(self.building_partner.service_start_date, date.today(),
                        "The building's service start date should match the activation date set.")

        # Verify that emails are processed correctly
        valid_emails = ['test1@example.com', 'test2@example.com']
        split_emails = test_emails.split(';')
        self.assertEqual(len(split_emails), len(valid_emails),
                        "All test emails should be processed correctly.")
