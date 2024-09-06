import logging
import os
import re
import time
from datetime import datetime
from .other_functions import (
    create_automation_vals,
    execute_custom_sql,
    disable_contract_views,
    create_products,
    create_contract_lines,
)

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
        for _, row in df.iterrows():
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

            for field_name, _ in fields_mapping.items():
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
                # time.sleep(0.1)
                try:
                    _logger.info(f"Purging records for wizard: {wizard.id}")
                    wizard.purge_all()
                except Exception as e:
                    _logger.error(f"Error purging records for wizard {wizard.id}: {e}")
        else:
            _logger.warning(f"No action found for wizard: {wizard_model_name}")

    def execute_remove_sql_wizard_nutrition_data(env):

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
            execute_custom_sql(env)
        except Exception as e:
            _logger.error(f"Error executing custom SQL: {e}")

        try:
            _logger.info("Importing nutrition data...")
            _import_nutrition_data(env)
        except Exception as e:
            _logger.error(f"Error importing nutrition data: {e}")

        for wizard in wizards:
            try:
                execute_wizard_action_and_purge(wizard)
                _logger.info("Executing wizard: %s..." % wizard)
            except Exception as e:
                _logger.error(f"Error processing wizard {wizard}: {e}")

    execute_remove_sql_wizard_nutrition_data(env)

    create_products(env)
    create_contract_lines(env)
    create_automation_vals(env)
    disable_contract_views(env)

    _logger.info("Post-init hook completed.")
    time.sleep(1)
