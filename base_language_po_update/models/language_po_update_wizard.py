import base64
import logging
import os
import re

_logger = logging.getLogger(__name__)

from odoo import fields, models


class LanguagePOUpdateWizard(models.TransientModel):
    _name = "language.po.update.wizard"
    _description = "Wizard to update PO files for selected modules and languages"

    modules = fields.Many2many(
        "ir.module.module",
        string="Modules",
        domain="[('state', '=', 'installed')]",
    )
    languages = fields.Many2many(
        "res.lang",
        string="Languages",
    )

    def action_update_multi_po_files(self):
        for module in self.modules:
            module_path = module.get_module_info(module.name).get("addons_path")
            module_path = os.path.join(module_path, module.name)
            os.chdir(module_path)
            if not module_path:
                continue
            elif not os.path.exists(os.path.join(module_path, "i18n")):
                os.makedirs(os.path.join(module_path, "i18n"))

            for lang in self.languages:
                po_file_path = os.path.join(module_path, "i18n", f"{lang.code}.po")

                unique_po_filename = self.generate_unique_filename(
                    f"{lang.code}_new", "po"
                )
                self.export_translations(
                    lang.code,
                    self.env.cr.dbname,
                    unique_po_filename,
                    module,
                    module_path,
                    po_file_path,
                )
                self.process_all_po_files(
                    lang.code,
                    os.path.join(module_path, "i18n", unique_po_filename),
                    module_path,
                )
                try:
                    source_file = os.path.join(
                        module_path, "/i18n/", unique_po_filename
                    )
                    if os.path.exists(source_file):

                        os.rename(
                            module_path + "/i18n/" + unique_po_filename, po_file_path
                        )
                        self.env.cr.commit()
                        _logger.info(
                            f"Archivo {unique_po_filename} exportado y movido correctamente para el módulo {module.name} y el idioma {lang.code}."
                        )
                except OSError as e:
                    _logger.error(
                        f"Error renaming/moving file {unique_po_filename} for module {module.name}: {e}"
                    )
                    continue
                except Exception as e:
                    _logger.error(
                        f"Unexpected error during commit or file operation for {module.name}: {e}"
                    )
                    continue
        return {
            "type": "ir.actions.act_window",
            "res_model": "language.po.update.wizard",
            "view_mode": "form",
            # 'view_id': self.env.ref('your_module.view_language_po_update_wizard_form').id,
            "target": "new",
            "context": {
                "default_modules": [(6, 0, self.modules.ids)],
                "default_languages": [(6, 0, self.languages.ids)],
            },
        }

    def generate_unique_filename(self, base_name, extension):
        """Generate a unique file name by appending a timestamp or random number."""
        counter = 0
        while True:
            if counter == 0:
                new_name = f"{base_name}.{extension}"
            else:
                new_name = f"{base_name}_{2^counter}_new.{extension}"
            if not os.path.exists(new_name):
                return new_name
            counter += 1

    def export_translations(
        self, language_code, db_name, new_filename, module, module_path, po_file_path
    ):
        _logger.info(f"Exportando traducciones...")
        export_wizard = self.env["base.language.export"].create(
            {
                "lang": language_code,
                "format": "po",
                "modules": [(6, 0, [module.id])],
            }
        )
        export_wizard.act_getfile()
        po_data = base64.b64decode(export_wizard.data)
        try:
            old_file_path = os.path.join(module_path, "i18n", language_code + ".po")
            if not os.path.exists(old_file_path):
                with open(old_file_path, "wb") as file:
                    file.write(po_data)
            new_file_path = os.path.join(module_path, "i18n", new_filename)
            with open(new_file_path, "wb") as file:
                file.write(po_data)

        except Exception as e:
            _logger.error(f"Error occurred: {e}")

    def add_translation_block(self, new_file, existing_file):
        """Add translation block from the new file to the existing file."""
        first_added_line = True
        msgstr_line = None
        intro_line = None
        previous_lines = []
        new_file_line_counter = 0
        idx = 0
        with open(new_file, encoding="utf-8") as nf:
            new_file_lines = nf.readlines()
            for line in new_file_lines:
                previous_lines.append(line)
                new_file_line_counter += 1
                if line.startswith("msgid"):
                    with open(existing_file, encoding="utf-8") as ef_check:
                        ef_check_lines = ef_check.readlines()
                        if not any(line.strip() in l for l in ef_check_lines):
                            reversed_previous_lines = list(reversed(previous_lines))
                            for prev_line in reversed_previous_lines:
                                if re.match(r"^#\.\ module", prev_line):
                                    idx = reversed_previous_lines.index(prev_line)
                                    break
                            idx = len(previous_lines) - idx - 1
                            previous_lines = previous_lines[idx:]

                            new_file_lines_temp = new_file_lines[new_file_line_counter:]
                            for after_line in new_file_lines_temp:
                                if re.match(r"^msgstr", after_line) and not msgstr_line:
                                    previous_lines.append(after_line)
                                    msgstr_line = line
                                elif (
                                    re.match(r"^\n", after_line)
                                    and msgstr_line
                                    and not intro_line
                                ):
                                    intro_line = after_line
                                    previous_lines.append(after_line)

                                    with open(
                                        existing_file, "a", encoding="utf-8"
                                    ) as ef:
                                        if first_added_line:
                                            previous_lines.insert(0, "\n")
                                            first_added_line = False
                                        ef.writelines(previous_lines)
                                    intro_line = None
                                    msgstr_line = None
                                    previous_lines = []
                                    break
                                    _logger.info(
                                        f"Bloque {previous_lines} añadido al archivo existente al final del archivo."
                                    )

    def process_all_po_files(self, language_code, new_file, module_path):
        """Process all .po files and add translations."""
        if not os.path.exists(new_file):
            _logger.info(f"El archivo nuevo {new_file} no se encontró.")
            return
        for file_name in os.listdir(module_path + "/i18n"):
            if file_name.endswith(language_code + ".po"):
                existing_file = file_name
                existing_file = module_path + "/i18n/" + existing_file
                self.add_translation_block(new_file, existing_file)
        try:
            os.remove(new_file)
            _logger.info(f"Archivo {new_file} eliminado correctamente.")
        except OSError as e:
            _logger.info(f"Error al eliminar el archivo {new_file}: {e}")
