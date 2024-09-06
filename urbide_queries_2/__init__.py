import logging
import os
import re
import time
from datetime import datetime

from odoo import api, SUPERUSER_ID

import numpy as np
import pandas as pd
import psycopg2

_logger = logging.getLogger(__name__)


def remove_files_before_install():
    files_to_remove = [
        "/opt/odoo/v16/github/oca/l10n-spain/l10n_es_ticketbai/migrations/16.0.1.0.1/pre-migration.py",
        "/opt/odoo/v16/github/oca/l10n-spain/l10n_es_ticketbai/migrations/16.0.1.0.1/post-migration.py",
        "/opt/odoo/v16/github/oca/contract/contract/migrations/16.0.2.0.0/post-migrate.py",
    ]

    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            _logger.info(f"Successfully removed {file_path}")
        except FileNotFoundError:
            _logger.warning(f"File {file_path} not found, skipping")
        except Exception as e:
            _logger.error(f"Error removing {file_path}: {str(e)}")


def _execute_custom_sql(env):
    queries = [
        # Insert into contract_contract from account_analytic_account
        """INSERT INTO contract_contract (
            id, partner_id, company_id, message_main_attachment_id,
            journal_id, contract_template_id, user_id, pricelist_id,
            recurring_interval, recurring_rule_type, recurring_invoicing_type,
            name, code, date_start, recurring_next_date,
            date_end, create_uid, write_uid,
            create_date, write_date, active, contract_type,
            invoice_partner_id, commercial_partner_id, generation_type
        )
        SELECT
            aa.id, aa.partner_id, aa.company_id, aa.message_main_attachment_id,
            aa.journal_id, aa.contract_template_id, aa.user_id, aa.pricelist_id,
            aa.recurring_interval, aa.recurring_rule_type, aa.recurring_invoicing_type,
            aa.name, aa.code, aa.date_start, aa.recurring_next_date,
            aa.date_end, aa.create_uid, aa.write_uid,
            aa.create_date, aa.write_date, aa.active, aa.type AS contract_type,
            p.id AS invoice_partner_id, p.commercial_partner_id, 'sale' AS generation_type
        FROM
            account_analytic_account aa
        JOIN
            res_partner p ON aa.partner_id = p.id
        WHERE NOT EXISTS (
            SELECT 1
            FROM contract_contract cc
            WHERE cc.id = aa.id
        );""",
        # Update product_template fields
        """UPDATE product_template
        SET nutrition_details = TRUE,
            ingredients_details = TRUE,
            allergy_details = TRUE;""",
        # Update ingredients_information
        """UPDATE product_template pt
        SET ingredients_information = COALESCE(
            (SELECT pp.ingredient_name->>'en_US'
                FROM product_product pp
                WHERE pp.product_tmpl_id = pt.id),
        '');""",
        # """ALTER TABLE ir_cron DROP CONSTRAINT IF EXISTS ir_cron_ir_actions_server_id_fkey;""",
        """DELETE FROM ir_cron WHERE ir_actions_server_id = 748;""",
        """DELETE FROM ir_cron WHERE ir_actions_server_id = 735;""",
        # """DELETE FROM ir_cron WHERE ir_actions_server_id = 734;""",
        # """DELETE FROM ir_cron WHERE ir_actions_server_id = 737;""",
        #         """ALTER TABLE ir_cron
        # ADD CONSTRAINT ir_cron_ir_actions_server_id_fkey
        # FOREIGN KEY (ir_actions_server_id) REFERENCES ir_act_server(id);
        #         """,
        #         """SELECT conname
        # FROM pg_constraint
        # WHERE conrelid = 'ir_cron'::regclass;
        #         """,
        """DELETE FROM date_range WHERE type_id = 1;""",
        """ALTER TABLE res_partner DROP CONSTRAINT IF EXISTS res_partner_zip_id_fkey;""",
        """UPDATE res_partner SET zip_id = NULL WHERE zip_id NOT IN (SELECT id FROM res_city);""",
        # """ALTER TABLE res_partner ADD CONSTRAINT res_partner_zip_id_fkey FOREIGN KEY (zip_id) REFERENCES res_city(id) ON DELETE SET NULL;""",
        """-- UPDATE para quitar error move_type_custom, sent y state (Undefined reading relation)
            UPDATE base_automation
            SET filter_domain = ''
            WHERE filter_domain LIKE '%move_type_custom%';
        """,
        """DELETE FROM ir_filters where domain ilike '%var_template_id%';""",
    ]

    for query in queries:
        _logger.info("Executing SQL query: %s", query)
        try:
            env.cr.execute(query)

            affected_rows = env.cr.rowcount
            _logger.info("Rows affected by query: %d", affected_rows)

        except Exception as e:
            _logger.error("Error executing query: %s, Error: %s\n\n", query, str(e))
            # env.cr.rollback()
            # _logger.info("Rolled back transaction due to error")
            raise


def _import_nutrition_data(env):
    fields_mapping = {
        "Azucares (g)": "carbo_sugars",
        "Azucares por UdM (g)": None,
        "Azucares por porción (g)": None,
        "Bread Units (BU)": None,
        "Bread Units per UoM (BU)": None,
        "Bread Units per portion (BU)": None,
        "Calorias (kJ)": "energy_joule",
        "Calorias (kcal)": "energy_calories",
        "Calorias por UdM (kJ)": None,
        "Calorias por UdM (kcal)": None,
        "Calorias por porción (kJ)": None,
        "Calorias por porción (kcal)": None,
        "Carbohidratos (g)": "carbohydrate",
        "Carbohidratos por UdM (g)": None,
        "Carbohidratos por porción (g)": None,
        "Fibra por UdM (g)": None,
        "Fibra por porción (g)": None,
        "Fibra vegetal (g)": "roughage",
        "Gluten-free": None,
        "Gramos por Porción": "portion_grams",
        "Grasa total (g)": "fat_total",
        "Grasa total por UdM (g)": None,
        "Grasa total por porción (g)": None,
        "Grasas saturadas (g)": "fat_saturated",
        "Grasas saturadas por UdM (g)": None,
        "Grasas saturadas por porcion (g)": None,
        "Lactose-free": None,
        "Porcentage Carb": "carb_percentage",
        "Porciones por UdM": None,
        "Porciones?": "portions",
        "Product Allergens (Abbr)": None,
        "Proteinas (g)": "protein",
        "Proteinas por UdM (g)": None,
        "Proteinas por porción (g)": None,
        "Sodio (g)": "sodium",
        "Sodio por UdM (g)": None,
        "Sodio por porción (g)": None,
        "Yeast-free": "yeast_free",
        "vegano": None,
        "Weight per UoM (g)": "norm_weight",
    }

    def extract_product_template_id(external_id):
        match = re.search(r"product_template_(\d+)", external_id)
        if match:
            return int(match.group(1))
        return None

    def check_product_template_exists(env, product_template_id):
        query = "SELECT id FROM product_template WHERE id = %s"
        env.cr.execute(query, (product_template_id,))
        return env.cr.fetchone() is not None

    def insert_nutrition_data_from_excel(env, df, total_lines):
        lines_inserted = 0
        start_time = time.time()
        time_per_line = []
        total_lines = len(fields_mapping) * total_lines
        for index, row in df.iterrows():
            external_id = row["External ID"]
            product_template_id = extract_product_template_id(external_id)
            if product_template_id is None:
                continue

            if not check_product_template_exists(env, product_template_id):
                _logger.info(
                    f"Skipping product_template_id {product_template_id}: not found in product_template table"
                )
                lines_inserted += len(fields_mapping)
                continue

            name = row["Nombre"]

            for field_name, db_column in fields_mapping.items():
                nutrition_value = row[field_name]
                if pd.isna(nutrition_value):
                    continue
                if isinstance(nutrition_value, bool):
                    _logger.info(
                        f"Nutrition value before: {field_name}, name: {name}, nutrition_value: {nutrition_value}"
                    )
                    nutrition_value = float(nutrition_value)
                elif isinstance(nutrition_value, str):
                    _logger.info(
                        f"Nutrition value before: {field_name}, name: {name}, nutrition_value: {nutrition_value}"
                    )
                    nutrition_value = None

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

                query = """
                    INSERT INTO product_nutrition (product_template_id, name, nutrition_value, create_uid, write_uid, create_date, write_date)
                    SELECT %s, %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM product_nutrition WHERE product_template_id = %s AND name = %s
                    );
                """

                _logger.debug("SQL Query: %s", query)
                _logger.debug(
                    "Values: %s",
                    (
                        product_template_id,
                        f"{name} {field_name}",
                        nutrition_value,
                        2,
                        2,
                        current_time,
                        current_time,
                        product_template_id,
                        f"{name} {field_name}",
                    ),
                )

                env.cr.execute(
                    query,
                    (
                        product_template_id,
                        f"{name} {field_name}",
                        nutrition_value,
                        2,
                        2,
                        current_time,
                        current_time,
                        product_template_id,
                        f"{name} {field_name}",
                    ),
                )

                affected_rows = env.cr.rowcount
                _logger.info("Rows affected by query: %d", affected_rows)

                verification_query = """
                    SELECT * FROM product_nutrition
                    WHERE product_template_id = %s AND name = %s;
                """
                env.cr.execute(
                    verification_query, (product_template_id, f"{name} {field_name}")
                )
                inserted_data = env.cr.fetchall()
                _logger.info("Inserted data: %s", inserted_data)

                lines_inserted += 1
                _logger.info(
                    f"Inserted data for field: {field_name}, name: {name}, nutrition_value: {nutrition_value}"
                )

                time_elapsed = time.time() - start_time
                lines_remaining = total_lines - lines_inserted

                if lines_remaining > 0:
                    time_per_line.append(time_elapsed / lines_inserted)

                    time_per_line_mean = np.mean(time_per_line)

                    if len(time_per_line) >= 50:
                        time_per_line.pop(0)

                    time_remaining = lines_remaining * time_per_line_mean

                    _logger.info(f"Time spent: {time_elapsed:.2f} seconds.")
                    _logger.info(
                        f"Estimated time remaining: {time_remaining:.2f} seconds"
                    )

        _logger.info(f"Total lines inserted: {lines_inserted}")

    file_path_1 = "/home/avanzosc/path_to_your_excel_file.xls"
    file_path_2 = "/opt/odoo/product_allergen_info_to_import.xls"

    if os.path.exists(file_path_1):
        file_path = file_path_1
    elif os.path.exists(file_path_2):
        file_path = file_path_2
    else:
        raise FileNotFoundError(f"Neither {file_path_1} nor {file_path_2} exist.")

    if not file_path.lower().endswith(".xls"):
        raise ValueError("The file must be an Excel file with a .xls extension.")

    df = pd.read_excel(file_path, engine="xlrd")
    total_lines = len(df)

    insert_nutrition_data_from_excel(env, df, total_lines)


def create_products(env):
    product_data = [
        {"name": "Martes", "price": 22},
        {"name": "Miércoles", "price": 22},
        {"name": "Jueves", "price": 22},
    ]

    products = {}
    _logger.info("Iniciando la creación de productos.")

    for data in product_data:
        _logger.info("Creando producto: %s con precio: %s", data["name"], data["price"])

        product_template = env["product.template"].create(
            {
                "name": data["name"],
                "list_price": data["price"],
            }
        )
        _logger.info("Plantilla de producto creada: %s", product_template.id)

        existing_product = env["product.product"].search(
            [
                ("product_tmpl_id", "=", product_template.id),
                ("combination_indices", "=", ""),
            ]
        )
        _logger.debug(
            "Buscando producto existente para plantilla ID: %s", product_template.id
        )

        if not existing_product:
            product = env["product.product"].create(
                {
                    "product_tmpl_id": product_template.id,
                }
            )
            _logger.info("Producto creado: %s", product.id)
        else:
            _logger.warning("Producto existente encontrado: %s", existing_product.id)

        products[data["name"].upper()] = product.id
        _logger.info(
            "Producto %s almacenado con ID: %s", data["name"].upper(), product.id
        )

    _logger.info("Productos creados: %s", list(products.keys()))
    return products


def create_contract_lines(env, products):
    contracts = env["contract.contract"].search([])
    _logger.info("Iniciando la creación de líneas de contrato.")
    _logger.info("Contratos encontrados: %s", [contract.name for contract in contracts])

    for contract in contracts:
        contract_name = contract.name.capitalize()
        _logger.info("Procesando contrato: %s", contract_name)

        if "JUEVES" in contract_name:
            product_id = products["JUEVES"]
        elif "MIÉRCOLES" in contract_name:
            product_id = products["MIÉRCOLES"]
        elif "MARTES" in contract_name:
            product_id = products["MARTES"]
        else:
            _logger.warning(
                "Contrato %s no coincide con ningún producto", contract_name
            )
            continue

        _logger.info(
            "Producto asignado para contrato: %s, producto ID: %s",
            contract_name,
            product_id,
        )

        _logger.info(
            "Creando línea de contrato para contrato: %s, producto ID: %s",
            contract_name,
            product_id,
        )

        contract_line = env["contract.line"].create(
            {
                "contract_id": contract.id,
                "product_id": product_id,
                "quantity": 1,
            }
        )
        _logger.info(
            "Línea de contrato creada con ID: %s para contrato: %s",
            contract_line.id,
            contract_name,
        )

    _logger.info(
        "Líneas de contrato creadas para contratos: %s",
        [contract.name for contract in contracts],
    )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Starting post-init hook...")

    def execute_wizard_action_and_purge(wizard_model_name):
        _logger.info(f"Processing wizard: {wizard_model_name}")
        wizard_model = env[wizard_model_name]
        action = wizard_model.get_wizard_action()
        if action:
            # Remove 'flags' key if present
            action.pop("flags", None)
            _logger.info(
                f"Creating action for wizard: {wizard_model_name} without flags"
            )
            env["ir.actions.act_window"].create(action)
            wizard_records = wizard_model.search([])
            _logger.info(
                f"Found {len(wizard_records)} records for wizard: {wizard_model_name}"
            )
            for wizard in wizard_records:
                time.sleep(0.1)
                try:
                    _logger.info(f"Purging records for wizard: {wizard.id}")
                    wizard.purge_all()
                except Exception as e:
                    _logger.error(f"Error purging records for wizard {wizard.id}: {e}")
        else:
            _logger.warning(f"No action found for wizard: {wizard_model_name}")

    wizards = [
        "cleanup.purge.wizard.column",
        "cleanup.purge.wizard.data",
        "cleanup.purge.wizard.field",
        "cleanup.purge.wizard.menu",
        "cleanup.purge.wizard.model",
        "cleanup.purge.wizard.module",
        # "cleanup.purge.wizard.property", Tal vez dará error
        "cleanup.purge.wizard.table",
        "cleanup.create_indexes.wizard",
    ]

    try:
        _logger.info("Removing files before install...")
        remove_files_before_install()
    except Exception as e:
        _logger.error(f"Error removing files before install: {e}")

    try:
        _logger.info("Executing custom SQL...")
        _execute_custom_sql(env)
    except Exception as e:
        _logger.error(f"Error executing custom SQL: {e}")

    try:
        _logger.info("Importing nutrition data...")
        # _import_nutrition_data(env)
    except Exception as e:
        _logger.error(f"Error importing nutrition data: {e}")

    for wizard in wizards:
        try:
            execute_wizard_action_and_purge(wizard)
        except Exception as e:
            _logger.error(f"Error processing wizard {wizard}: {e}")

    _logger.info("Post-init hook completed.")
    time.sleep(1)

    automation_vals_1 = {
        "name": "Actualizar fecha de entrega en pedidos de venta",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "trigger": "on_create",
        "code": """
for record in records:
    record.write({
        "commitment_date": expected_date,
        "picking_type_id": record.warehouse_id.out_type_id.id,
    })
    """,
        "active": True,
    }

    _logger.info("Creating automation rule: %s", automation_vals_1["name"])
    env["base.automation"].create(automation_vals_1)

    automation_vals_2 = {
        "name": "Marcar carro abandonado al crear pedido",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "trigger": "on_create_or_write",
        "code": """
for record in records:
    website = env['website'].search([('id', '=', '1')])
    if website:
        record.write({
            'website_id': website.id
        })
    else:
        raise ValueError("El sitio web con ID 1 no existe.")
    """,
        "active": True,
    }

    _logger.info("Creating automation rule: %s", automation_vals_2["name"])
    env["base.automation"].create(automation_vals_2)

    expected_date_id_ref = env["ir.model.fields"].search(
        [("model", "=", "sale.order"), ("name", "=", "expected_date")]
    )
    calendar = env["resource.calendar"].search([], limit=1).ensure_one()

    if not expected_date_id_ref:
        _logger.warning("Expected date field not found.")
    if not calendar:
        _logger.warning("Standard 40 hours/week calendar not found.")

    automation_vals_3 = {
        "name": "Confirmar el pedido 2 días antes de fecha de entrega",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "trigger": "on_time",
        "filter_domain": '["&", ("expected_date", "!=", False), "|", ("state", "=", "draft"), ("state", "=", "sent")]',
        "trg_date_id": expected_date_id_ref.id,
        "trg_date_range": -2,
        "trg_date_calendar_id": calendar.id,
        "code": """
for record in records:
    record.action_confirm()
""",
        "active": True,
    }
    _logger.info("Creating automation rule: %s", automation_vals_3["name"])
    env["base.automation"].create(automation_vals_3)
    time.sleep(1)

    action_server_vals_4 = {
        "name": "Marcar carro abandonado",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "code": """
    for record in records:
        website = env['website'].search([('name', '=', 'Urbide')], limit=1)
        if website:
            record.write({
                'website_id': website.id
            })
    """,
        "binding_model_id": env.ref("sale.model_sale_order").id,
    }

    _logger.info("Creating action server: %s", action_server_vals_4["name"])
    env["ir.actions.server"].create(action_server_vals_4)

    action_server_vals_5 = {
        "name": "Enviar correo electrónico de recuperación de cesta",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "code": """
    if records:
        action = records.action_recovery_email_send()
    """,
        "binding_model_id": env.ref("sale.model_sale_order").id,
    }

    _logger.info("Creating action server: %s", action_server_vals_5["name"])
    env["ir.actions.server"].create(action_server_vals_5)

    mass_editing_vals = {
        "name": "Actualizar Fecha de Entrega",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "code": """
    for record in records:
        if 'commitment_date' in record:
            record.write({
                "commitment_date": new_date,  # Define 'new_date' según tu lógica
            })
    """,
    }

    _logger.info("Creating mass editing action: %s", mass_editing_vals["name"])
    env["ir.actions.server"].create(mass_editing_vals)

    products = create_products(env)
    create_contract_lines(env, products)
