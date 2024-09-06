import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _execute_custom_sql(env):
    queries = [
        """UPDATE ir_module_module
        SET state = 'uninstalled'
        WHERE name IN ('contract', 'l10n_es_aeat', 'account_reports', 'l10n_es_aeat_mod303');""",
        """DELETE FROM ir_ui_view WHERE arch_db ->> 'en_US' LIKE '%head_website%';""",
        # Modify res_partner related city
        # """ALTER TABLE res_partner DROP CONSTRAINT IF EXISTS res_partner_zip_id_fkey;""",
        # """UPDATE res_partner SET zip_id = NULL WHERE zip_id NOT IN (SELECT id FROM res_city);""",
        # """DO $$
        #     BEGIN
        #         -- Check if the res_city table exists
        #         IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'res_city') THEN
        #             -- Execute the UPDATE query only if res_city exists
        #             UPDATE res_partner
        #             SET zip_id = NULL
        #             WHERE zip_id NOT IN (SELECT id FROM res_city);
        #             ALTER TABLE res_partner
        #             ADD CONSTRAINT res_partner_zip_id_fkey
        #             FOREIGN KEY (zip_id) REFERENCES res_city(id) ON DELETE SET NULL;
        #         END IF;
        #     END $$;
        # """,
        # Update stock location
        """UPDATE stock_location SET scrap_location = FALSE WHERE scrap_location = TRUE AND name LIKE 'Stock';""",
        # Update website menu
        """UPDATE website_menu SET url = '/shop' WHERE url = 'https://urbide.eu/shop';""",
        # Delete unnecessary views
        """DELETE FROM ir_ui_view
        WHERE inherit_id IN (
            SELECT id FROM ir_ui_view
            WHERE key ILIKE '%wine_store.%'
               OR name ILIKE '%sale order classification%'
               OR arch_fs ILIKE '%product_allergens_labeling%'
               OR arch_fs ILIKE '%product_nutrition/%'
               OR arch_fs ILIKE '%acy_urbide/%'
               OR arch_fs ILIKE '%purchase_small_supplier/%'
               OR arch_fs ILIKE '%partner_delivery_point/%'
               OR arch_fs ILIKE '%website_product_pack/%'
               OR arch_fs ILIKE '%account_reports/%'
               OR arch_fs ILIKE '%website_sale_allergens/%'
               OR arch_fs ILIKE '%kc_wishlist/%'
               OR arch_fs ILIKE '%account_reports/%'
        );""",
        """DELETE FROM ir_asset WHERE name LIKE '%l10n_es_aeat%';""",
        # Remove unnecessary assets
        """DELETE FROM ir_asset
        WHERE path ILIKE '/wine_store/%'
           OR path ILIKE '/website_back2top/%'
           OR path ILIKE '/website_cookie_notice/%'
           OR path ILIKE '/kc_wishlist/%'
           OR path ILIKE '/mass_mailing_custom_unsubscribe/%'
           OR path ILIKE '/website_product_pack/%'
           OR path ILIKE '/website_style_manager/%'
           OR path ILIKE '/web_decimal_numpad_dot/%'
           OR path ILIKE '/support_branding/%'
           OR path ILIKE '/web_export_view/%'
           OR path ILIKE '/date_range/%'
           OR path ILIKE '/web_sheet_full_width/%'
           ;""",
        # Remove move_type_custom error
        """DELETE FROM ir_rule WHERE domain_force::text LIKE '%move_type_custom%';""",
        # Remove header error
        """DELETE FROM ir_ui_view WHERE arch_db::text LIKE '%//header//div[2]%';""",
        """UPDATE ir_ui_view
            SET active = False
            WHERE id IN (
                SELECT v.id
                FROM ir_ui_view v
                LEFT JOIN ir_model_data md ON md.res_id = v.id
                WHERE md.model = 'ir.ui.view'
                AND (md.module LIKE '%website_product_pack%' OR md.module LIKE '%acy_urbide%')
            );""",
        # Ejecutar esto y hacer update=all si la pantalla queda blanca en el backend
        # """UPDATE ir_module_module SET state = 'uninstalled' WHERE name ILIKE '%web_enterprise%';""",
    ]

    for query in queries:
        try:

            _logger.info("Executing SQL query: %s", query)
            env.cr.execute(query)
            affected_rows = env.cr.rowcount
            _logger.info(
                "Query executed successfully, affected rows: %d", affected_rows
            )
            import time

            time.sleep(0.4)
        except Exception as e:
            _logger.error("Error executing queries, rolling back. Error: %s", str(e))
            # env.cr.rollback()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _execute_custom_sql(env)
