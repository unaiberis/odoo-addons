.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://opensource.org/licenses/LGPL-3.0
   :alt: License: LGPL-3

=======================================================
Base Language PO Update
=======================================================

Overview
========

The **Base Language PO Update** module provides a wizard to update PO (Portable Object) files for selected Odoo modules and languages. It facilitates the process of exporting and merging translations into existing PO files, ensuring that translations are up-to-date and complete across different languages.

Features
========

- **Wizard for PO File Update**:
  
  - Allows users to select modules and languages to update PO files.

- **Export Translations**:
  
  - Exports translations from the Odoo database to PO files.

- **Merge Translations**:
  
  - Merges new translations into existing PO files, preserving existing content.

Usage
=====

1. **Install the Module**:
   
   - Install the module through the Odoo apps interface or by placing it in your Odoo addons directory.

2. **Access the Wizard**:

   - Go to the **Settings** menu and find the **Language PO Update Wizard** under the **Translators** category.

3. **Select Modules and Languages**:

   - Choose the modules and languages you want to update.

4. **Update PO Files**:

   - Click on the **Update** button to export and merge translations.

Configuration
=============

- **User Permissions**:
  
  - Ensure that the user has the necessary permissions to access and modify PO files.

Testing
=======

Test the following scenarios:

- **Run the Wizard**:
  
  - Verify that the wizard displays the available modules and languages correctly.

- **Check PO Files**:

  - Ensure that the PO files are updated correctly with new translations and that no existing translations are lost.

- **File Operations**:

  - Confirm that the PO files are correctly exported, merged, and removed as expected.

Bug Tracker
===========

For bugs and issues, please visit `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_ to report or track issues.

Credits
=======

Contributors
------------

* Unai Beristain <unaiberistain@avanzosc.es>

* Ana Juaristi <anajuaristi@avanzosc.es>

Please contact contributors for module-specific questions, but direct support requests should be made through the official channels.

License
=======
This project is licensed under the LGPL-3 License. For more details, please refer to the LICENSE file or visit <https://opensource.org/licenses/LGPL-3.0>.
