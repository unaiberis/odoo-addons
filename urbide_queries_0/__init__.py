import logging
from odoo import api, SUPERUSER_ID

# Initialize logger
_logger = logging.getLogger(__name__)

def _generate_queries(fields_and_models):
    queries = []
    for field_name, model_name in fields_and_models:
        queries.append(
            f"""DELETE FROM ir_model_fields WHERE name = '{field_name}' AND model = '{model_name}';"""
        )
        queries.append(
            f"""DELETE FROM ir_model_data WHERE model = 'ir.model.fields' AND name LIKE '%{field_name}%';"""
        )
        queries.append(
            f"""DELETE FROM ir_rule WHERE domain_force LIKE '%{field_name}%';"""
        )
        queries.append(
            f"""DELETE FROM ir_model_access WHERE model_id IN (
                SELECT id FROM ir_model WHERE model = '{model_name}');"""
        )
        queries.append(
            f"""DELETE FROM ir_ui_view WHERE arch_db::text LIKE '%{field_name}%';"""
        )
        queries.append(
            f"""DELETE FROM ir_model_data WHERE name LIKE '%{field_name}%';"""
        )
    return queries

def _execute_custom_sql(env):
    # Define field and model pairs
    fields_and_models = [
        ('contract_pregenerate_days', 'res.company'),
        ('acc_country_id', 'res.partner.bank'),
        ('better_zip_id', 'res.company')
    ]

    queries = _generate_queries(fields_and_models)
    
    for query in queries:
        _logger.info("Executing SQL query: %s", query)
        try:
            env.cr.execute(query)
            row_count = env.cr.rowcount
            _logger.info("Query executed successfully. %d rows affected.\n\n", row_count)
            import time
            time.sleep(0.2)
        except Exception as e:
            _logger.error("Error executing custom SQL: %s", e)
            # env.cr.rollback()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _execute_custom_sql(env)



    # EXECUTE format(
    #     'DELETE FROM ir_module_module WHERE name IN (
    #         ''contract'', ''l10n_es_aeat'', ''account_reports'', 
    #         ''l10n_es_aeat_mod303'');'
    # );
    # EXECUTE format(
    #     'DELETE FROM ir_model_data WHERE module = ''base'' AND name IN (
    #         ''module_account_reports'', ''module_contract'', 
    #         ''module_l10n_es_aeat'', ''module_l10n_es_aeat_mod303'');'
    # );
