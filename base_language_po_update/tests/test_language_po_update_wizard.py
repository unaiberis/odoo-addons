import os

from odoo.tests import TransactionCase


class TestLanguagePOUpdateWizard(TransactionCase):
    def setUp(self):
        super().setUp()

        # Set up test data
        self.Module = self.env["ir.module.module"]
        self.Lang = self.env["res.lang"]
        self.LanguagePOUpdateWizard = self.env["language.po.update.wizard"]

        # Create test module
        self.module = self.Module.create(
            {
                "name": "Test Module",
                "state": "installed",
            }
        )

        # Create test language
        self.language = self.Lang.create(
            {
                "name": "Test Language",
                "code": "test_lang",
            }
        )

        # Add the test module to the database
        self.module.update(
            {
                "state": "installed",
            }
        )

    def test_action_update_multi_po_files(self):
        wizard = self.LanguagePOUpdateWizard.create(
            {
                "modules": [(6, 0, [self.module.id])],
                "languages": [(6, 0, [self.language.id])],
            }
        )

        # Execute the action
        result = wizard.action_update_multi_po_files()

        # Check if the action returns the correct action
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "language.po.update.wizard")

        # Additional checks can be added here depending on what `action_update_multi_po_files` does
        # For instance, checking if files were created or moved correctly.

    def test_generate_unique_filename(self):
        wizard = self.LanguagePOUpdateWizard.create({})

        # Create a file with a specific name to test uniqueness
        base_name = "test_file"
        extension = "po"

        filename1 = wizard.generate_unique_filename(base_name, extension)
        filename2 = wizard.generate_unique_filename(base_name, extension)

        # Check if the filenames are different
        self.assertNotEqual(filename1, filename2)
        self.assertTrue(filename1.endswith(f"_{2**0}_new.{extension}"))
        self.assertTrue(filename2.endswith(f"_{2**1}_new.{extension}"))

    def test_export_translations(self):
        wizard = self.LanguagePOUpdateWizard.create({})

        # Define file paths and module
        module = self.module
        module_path = "/tmp/test_module"
        lang_code = self.language.code
        po_file_path = f"{module_path}/i18n/{lang_code}.po"

        # Create a dummy export_wizard data
        wizard.export_translations(
            lang_code, self.env.cr.dbname, "test.po", module, module_path, po_file_path
        )

        # Check if the file has been created
        self.assertTrue(os.path.exists(po_file_path))

        # Clean up
        if os.path.exists(po_file_path):
            os.remove(po_file_path)

    def test_add_translation_block(self):
        wizard = self.LanguagePOUpdateWizard.create({})

        new_file = "/tmp/new.po"
        existing_file = "/tmp/existing.po"

        # Create dummy files
        with open(new_file, "w") as nf:
            nf.write('msgid "Hello"\nmsgstr "Hola"\n')

        with open(existing_file, "w") as ef:
            ef.write('msgid "Hello"\nmsgstr "Hello"\n')

        wizard.add_translation_block(new_file, existing_file)

        # Check if the content was added to the existing file
        with open(existing_file) as ef:
            content = ef.read()

        self.assertIn('msgid "Hello"', content)
        self.assertIn('msgstr "Hola"', content)

        # Clean up
        if os.path.exists(new_file):
            os.remove(new_file)
        if os.path.exists(existing_file):
            os.remove(existing_file)
