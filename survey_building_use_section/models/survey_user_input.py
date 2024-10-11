# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    inspected_building_id = fields.Many2one(
        "res.partner",
        string="Inspected Building",
    )
    maintainer_id = fields.Many2one(
        "res.partner",
        string="Maintainer",
        related="inspected_building_id.maintainer_id",
    )
    maintainer_emi = fields.Char(
        string="Maintainer EMI",
        related="maintainer_id.emi",
    )
    installer_id = fields.Many2one(
        "res.partner",
        string="Installer",
        related="inspected_building_id.installer_id",
    )
    installer_epi = fields.Char(
        string="Installer EPI",
        related="installer_id.epi",
    )
    administrator_id = fields.Many2one(
        "res.partner",
        string="Administrator",
        related="inspected_building_id.administrator_id",
    )
    configuration = fields.Selection(
        string="Configuration",
        related="building_section_id.configuration",
        store=True,
    )
    building_section_id = fields.Many2one(
        "building.section",
        string="Building Section/Area",
    )
    section_ids = fields.One2many(
        "building.section",
        "partner_id",
        string="Inspected Building Section/Area",
        related="inspected_building_id.building_section_ids",
    )
    building_use_id = fields.Many2one(
        "building.use",
        string="Building type",
        related="inspected_building_id.building_use_id",
        store=True,
    )
    is_industrial = fields.Boolean(
        string="Industrial",
        related="building_use_id.is_industrial",
        store=True,
    )
    risk = fields.Char(
        string="Risk",
        related="building_section_id.risk",
        store=True,
    )
    area = fields.Float(
        string="Superficie",
        related="building_section_id.area",
        store=True,
    )
    file_number = fields.Char(
        string="File Number",
        related="inspected_building_id.file_number",
        store=True,
    )
    number_of_floors = fields.Char(
        string="Number of Plants",
        related="inspected_building_id.number_of_floors",
        store=True,
    )
    installation_number = fields.Char(
        string="Installation Number",
        related="inspected_building_id.installation_number",
    )
    acta_id = fields.Many2one(
        "acta",
        string="Act",
    )
    acta_number = fields.Char(
        related="acta_id.acta_number",
    )
    inspection_start_date = fields.Date(
        related="acta_id.inspection_start_date",
    )
    inspection_end_date = fields.Date(
        related="acta_id.inspection_end_date",
    )
    inspector_id = fields.Many2one(
        related="acta_id.inspector_id",
    )
    inspection_type = fields.Selection(
        related="acta_id.inspection_type",
    )
    date_deficiency_correction = fields.Date()
    next_inspection_date = fields.Date()
    installed_equipment_ids = fields.Many2many(
        "installed.equipment",
        string="Installed Equipment",
    )

    # Project
    project_title = fields.Char(
        string="Project Title",
        related="inspected_building_id.project_title",
    )
    project_author_id = fields.Many2one(
        "res.partner",
        string="Project Author",
        related="inspected_building_id.project_author_id",
    )
    project_author_degree = fields.Char(
        string="Project Author Degree",
        related="inspected_building_id.project_author_id.degree_title",
    )
    project_author_license = fields.Char(
        string="Project Author License",
        related="inspected_building_id.project_author_id.membership_number",
    )
    project_approved_date = fields.Date(
        string="Project Approved Date",
        related="inspected_building_id.project_approved_date",
    )

    certification_date = fields.Date(
        string="Certification Date",
        related="inspected_building_id.certification_date",
    )

    # Certificate of Final Work Direction
    dof_author_id = fields.Many2one(
        "res.partner",
        string="Director of Works Author",
        related="inspected_building_id.dof_author_id",
    )
    dof_author_degree = fields.Char(
        string="Director of Works Author Degree",
        related="inspected_building_id.dof_author_id.degree_title",
    )
    dof_author_license = fields.Char(
        string="Director of Works Author License",
        related="inspected_building_id.dof_author_id.membership_number",
    )
    dof_approved_date = fields.Date(
        string="Director of Works Approved Date",
        related="inspected_building_id.dof_approved_date",
    )

    survey_report_fussion = fields.Many2many(
        "survey.user_input",
        relation="survey_report_fussion_rel",
        column1="survey_report_fussion_id",
        column2="survey_report_id",
    )

    @api.model_create_multi
    def create(self, vals_list):
        inputs = super().create(vals_list)
        for input in inputs:
            if "building" in self.env.context:
                input.inspected_building_id = self.env.context.get("building").id
        return inputs

    def action_start_survey(self):
        current_user_partner = self.env.user.partner_id

        if current_user_partner:
            # Asignar el ID del socio asociado con el usuario actual al partner_id del survey_user_input
            self.partner_id = current_user_partner.id
        else:
            # Usuario administrador es id = 3
            self.partner_id = 3

        # Obtener la URL completa de la solicitud actual
        full_url = request.httprequest.url

        # Encontrar el índice del primer punto y el primer slash después de ese punto
        dot_index = full_url.find(".")
        slash_index = full_url.find("/", dot_index)

        base_url = False

        # Extraer la URL base
        if dot_index != -1 and slash_index != -1:
            base_url = full_url[:slash_index]

        if not base_url:
            base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        survey_id = self.survey_id
        access_token = survey_id.access_token
        answer_token = self.access_token
        url = "{}/survey/start/{}?answer_token={}".format(
            base_url, access_token, answer_token
        )
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def action_duplicate_survey_user_input(self):
        survey_user_input_line_obj = self.env["survey.user_input.line"]

        if not self:
            active_ids = self.env.context.get("active_ids", [])
            if not active_ids:
                _logger.error("No records found in self or active_ids")
                return False
            user_inputs = self.env["survey.user_input"].browse(active_ids)
        else:
            user_inputs = self

        for user_input in user_inputs:
            _logger.info("Duplicating survey user input ID: %s", user_input.id)
            new_user_input = None
            try:
                new_user_input = user_input.copy(
                    {
                        "state": "new",
                    }
                )
                _logger.info(
                    "Successfully created new survey user input with ID: %s from original ID: %s",
                    new_user_input.id,
                    user_input.id,
                )
            except Exception as e:
                _logger.error(
                    "Error duplicating survey user input ID: %s. Error: %s",
                    user_input.id,
                    e,
                )
                continue

            if new_user_input:
                try:
                    related_lines = survey_user_input_line_obj.search(
                        [("user_input_id", "=", user_input.id)]
                    )
                    _logger.info(
                        "Found %s related lines for survey user input ID: %s",
                        len(related_lines),
                        user_input.id,
                    )

                    for line in related_lines:
                        try:
                            new_line = line.copy({"user_input_id": new_user_input.id})
                            _logger.info(
                                "Successfully duplicated survey user input line ID: %s as new ID: %s for user input ID: %s",
                                line.id,
                                new_line.id,
                                new_user_input.id,
                            )
                        except Exception as e:
                            _logger.error(
                                "Error duplicating survey user input line ID: %s for user input ID: %s. Error: %s",
                                line.id,
                                user_input.id,
                                e,
                            )
                except Exception as e:
                    _logger.error(
                        "Error searching for related lines for survey user input ID: %s. Error: %s",
                        user_input.id,
                        e,
                    )

            if new_user_input and len(user_inputs) == 1:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Survey User Input",
                    "res_model": "survey.user_input",
                    "view_mode": "form",
                    "res_id": new_user_input.id,
                    "target": "current",
                }

        return True
