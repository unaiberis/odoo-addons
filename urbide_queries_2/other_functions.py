import time
from logging import getLogger

_logger = getLogger(__name__)


def create_automation_vals(env):
    automation_vals_1 = {
        "name": "Actualizar fecha de entrega = fecha de pedido + X días y punto de entrega",
        "model_id": env.ref("sale.model_sale_order").id,
        "state": "code",
        "trigger": "on_create",
        "code": """
for record in records:
    record.write(
        {"commitment_date": record.expected_date}
    )
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
        "filter_domain": '["|", ("state", "=", "draft"), ("state", "=", "sent")]',
        "trg_date_id": expected_date_id_ref.id,
        "trg_date_range": -2,
        "trg_date_range_type": "day",
        "trg_date_calendar_id": calendar.id,
        "code": """
for record in records:
    if record.expected_date and record.state in ['draft', 'sent']:
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


def execute_custom_sql(env):
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
        #         """UPDATE res_partner
        # SET zip_id = NULL
        # WHERE zip_id IS NOT NULL
        #   AND EXISTS (SELECT 1 FROM res_city)
        #   AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'res_city');
        #         """,
        """UPDATE res_partner SET zip_id = NULL WHERE zip_id NOT IN (SELECT id FROM res_city);""",
        # """ALTER TABLE res_partner ADD CONSTRAINT res_partner_zip_id_fkey FOREIGN KEY (zip_id) REFERENCES res_city(id) ON DELETE SET NULL;""",
        """-- UPDATE para quitar error move_type_custom, sent y state (Undefined reading relation)
            UPDATE base_automation
            SET filter_domain = ''
            WHERE filter_domain LIKE '%move_type_custom%';
        """,
        """DELETE FROM ir_filters where domain ilike '%var_template_id%';""",
        # """UPDATE mail_template
        #     SET subject = '{"en_US": "{{ object.company_id.name }} Factura (Ref {{ object.name or ''n/a'' }})", "es_ES": "{{ object.company_id.name }} Factura (Ref {{ object.name or ''n/a'' }})", "eu_ES": "{{ object.company_id.name }} Faktura (Ref {{ object.name or ''n/a'' }})"}'
        #     WHERE id = 5;
        # """,
        """UPDATE res_users SET password = 'urb1d3_pwd' WHERE login = 'admin';""",
#         """UPDATE mail_template
# SET subject = '{
#     "en_US": "{{ object.company_id.name }} Updated Invoice (Ref {{ object.name or '''' }} )",
#     "es_ES": "{{ object.company_id.name }} Factura (Ref {{ object.name or '''' }} )",
#     "eu_ES": "{{ object.company_id.name }} Faktura (Ref {{ object.name or '''' }} )"
# }'
# WHERE id = 5;
#         """,
#         """

#         UPDATE mail_template
# SET report_name = '{
#     "en_US": "Invoice_{{ (object.name or '''').replace(''/'',''_'') }}{{ object.state == ''draft'' and ''_draft'' or '''' }}",
#     "es_ES": "Invoice_{{ (object.name or '''').replace(''/'',''_'') }}{{ object.state == ''draft'' and ''_draft'' or '''' }}",
#     "eu_ES": "Invoice_{{ (object.name or '''').replace(''/'',''_'') }}{{ object.state == ''draft'' and ''_draft'' or '''' }}"
# }'
# WHERE id = 5;


#         """,
#         """
# UPDATE mail_template
# SET body_html = to_json($json${
#     "en_US": "<div style=\"margin: 0px; padding: 0px;\"><p style=\"margin: 0px; padding: 0px; font-size: 13px;\">Dear<t t-if=\"object.partner_id.parent_id\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t> (<t t-out=\"object.partner_id.parent_id.name or ''\">Azure Interior</t>),</t><t t-else=\"\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t>,</t><br /><br />Here is your<t t-if=\"object.name\">invoice <span style=\"font-weight:bold;\" t-out=\"object.name or ''\">INV/2021/05/0005</span></t><t t-else=\"\">invoice</t><t t-if=\"object.invoice_origin\">(with reference: <t t-out=\"object.invoice_origin or ''\">SUB003</t>)</t>amounting in <span style=\"font-weight:bold;\" t-out=\"format_amount(object.amount_total, object.currency_id) or ''\">$ 143,750.00</span> from <t t-out=\"object.company_id.name or ''\">YourCompany</t>.<t t-if=\"object.payment_state in ('paid', 'in_payment')\">This invoice is already paid.</t><t t-else=\"\">Please remit payment at your earliest convenience.<t t-if=\"object.payment_reference\"><br /><br />Please use the following communication for your payment: <span style=\"font-weight:bold;\" t-out=\"object.payment_reference or ''\">INV/2021/05/0005</span>.</t></t><br /><br />Do not hesitate to contact us if you have any questions.<t t-if=\"not is_html_empty(object.invoice_user_id.signature)\"><br /><br /><t t-out=\"object.invoice_user_id.signature or ''\">--<br/>Mitchell Admin</t></t></p></div>",
#     "es_EU": "<div style=\"margin: 0px; padding: 0px;\"><p style=\"margin: 0px; padding: 0px; font-size: 13px;\">Maitea<t t-if=\"object.partner_id.parent_id\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t> (<t t-out=\"object.partner_id.parent_id.name or ''\">Azure Interior</t>),</t><t t-else=\"\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t>,</t><br /><br />Hona hemen zure<t t-if=\"object.name\"> faktura <span style=\"font-weight:bold;\" t-out=\"object.name or ''\">INV/2021/05/0005</span></t><t t-else=\"\">faktura</t><t t-if=\"object.invoice_origin\">(erreferentzia: <t t-out=\"object.invoice_origin or ''\">SUB003</t>)</t>amounting in <span style=\"font-weight:bold;\" t-out=\"format_amount(object.amount_total, object.currency_id) or ''\">$ 143,750.00</span> from <t t-out=\"object.company_id.name or ''\">YourCompany</t>.<t t-if=\"object.payment_state in ('paid', 'in_payment')\">Faktura hau jada ordainduta dago.</t><t t-else=\"\">Mesedez, ordaindu ahalik eta lasterren.<t t-if=\"object.payment_reference\"><br /><br />Mesedez, erabili zure ordainketarako komunikazioa: <span style=\"font-weight:bold;\" t-out=\"object.payment_reference or ''\">INV/2021/05/0005</span>.</t></t><br /><br />Edozein galdera izanez gero, jarri gurekin harremanetan.<t t-if=\"not is_html_empty(object.invoice_user_id.signature)\"><br /><br /><t t-out=\"object.invoice_user_id.signature or ''\">--<br/>Mitchell Admin</t></t></p></div>",
#     "es_ES": "<div style=\"margin: 0px; padding: 0px;\"><p style=\"margin: 0px; padding: 0px; font-size: 13px;\">Estimado<t t-if=\"object.partner_id.parent_id\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t> (<t t-out=\"object.partner_id.parent_id.name or ''\">Azure Interior</t>),</t><t t-else=\"\"><t t-out=\"object.partner_id.name or ''\">Brandon Freeman</t>,</t><br /><br />Aquí está su<t t-if=\"object.name\"> factura <span style=\"font-weight:bold;\" t-out=\"object.name or ''\">INV/2021/05/0005</span></t><t t-else=\"\">factura</t><t t-if=\"object.invoice_origin\">(con referencia: <t t-out=\"object.invoice_origin or ''\">SUB003</t>)</t>amounting in <span style=\"font-weight:bold;\" t-out=\"format_amount(object.amount_total, object.currency_id) or ''\">$ 143,750.00</span> from <t t-out=\"object.company_id.name or ''\">YourCompany</t>.<t t-if=\"object.payment_state in ('paid', 'in_payment')\">Esta factura ya está pagada.</t><t t-else=\"\">Por favor, realice el pago a la mayor brevedad posible.<t t-if=\"object.payment_reference\"><br /><br />Por favor, utilice la siguiente comunicación para su pago: <span style=\"font-weight:bold;\" t-out=\"object.payment_reference or ''\">INV/2021/05/0005</span>.</t></t><br /><br />No dude en ponerse en contacto con nosotros si tiene alguna pregunta.<t t-if=\"not is_html_empty(object.invoice_user_id.signature)\"><br /><br /><t t-out=\"object.invoice_user_id.signature or ''\">--<br/>Mitchell Admin</t></t></p></div>"
# }$json$::jsonb)
# WHERE id = 5;



# """,
    ]

    for i, query in enumerate(queries):
        _logger.info("Executing SQL query %d: %s", i + 1, query)
        try:
            # Create a savepoint before executing the query
            env.cr.execute("SAVEPOINT urbide_queries_2_savepoint;")
            env.cr.execute(query)

            # Log the number of affected rows
            affected_rows = env.cr.rowcount
            _logger.info("Rows affected by query %d: %d", i + 1, affected_rows)

        except Exception as e:
            _logger.error(
                "Error executing query %d: %s, Error: %s", i + 1, query, str(e)
            )
            # Rollback to the savepoint instead of raising an error
            env.cr.execute("ROLLBACK TO SAVEPOINT urbide_queries_2_savepoint;")
        time.sleep(1)

    # Optional: Release the savepoint at the end
    env.cr.execute("RELEASE SAVEPOINT urbide_queries_2_savepoint;")
    time.sleep(10)


def disable_contract_views(env):
    views_to_disable = [
        "contract.account_analytic_account_recurring_form_form",
        "contract.view_account_analytic_account_journal_tree",
        "contract.view_account_analytic_account_contract_search",
        "contract.account_analytic_account_recurring_form_form",
    ]

    for view_xml_id in views_to_disable:
        view = env.ref(view_xml_id, raise_if_not_found=False)
        if view:
            view.write({"active": False})


def create_products(env):
    product_data = [
        {"name": "Martes"},
        {"name": "Miércoles"},
        {"name": "Jueves"},
    ]

    products = {}
    _logger.info("Iniciando la creación de productos.")

    for data in product_data:
        _logger.info("Creando producto: %s con precio: 22", data["name"])

        tax = env["account.tax"].browse(168)
        product_template = env["product.template"].create(
            {
                "name": data["name"],
                "list_price": 22,
                "is_basket": True,
                "detailed_type": "product",
                **({"taxes_id": [(6, 0, [tax.id])]} if tax.exists() else {}),
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
        product = False
        if not existing_product:
            product = env["product.product"].create(
                {
                    "product_tmpl_id": product_template.id,
                }
            )
            _logger.info("Producto creado: %s", product.id)
        else:
            _logger.warning("Producto existente encontrado: %s", existing_product.id)

        products[data["name"].upper()] = (
            product.id if product and hasattr(product, "id") else False
        )
        _logger.info("Producto %s almacenado", data["name"].upper())

    _logger.info("Productos creados: %s", list(products.keys()))
    return products


def create_contract_lines(env):
    contracts = env["contract.contract"].search([])
    _logger.info("Iniciando la creación de líneas de contrato.")
    _logger.info("Contratos encontrados: %s", [contract.name for contract in contracts])

    for contract in contracts:
        contract_name = contract.name.upper()
        _logger.info("Procesando contrato: %s", contract_name)

        if "JUEVES" in contract_name:
            product = env["product.product"].search(
                [("name", "=", "Jueves"), ("product_tmpl_id.list_price", "=", 22)],
                limit=1,
            )
            product_id = product.id if product else None
        elif "MIÉRCOLES" in contract_name:
            product = env["product.product"].search(
                [("name", "=", "Miércoles"), ("product_tmpl_id.list_price", "=", 22)],
                limit=1,
            )
            product_id = product.id if product else None
        elif "MARTES" in contract_name:
            product = env["product.product"].search(
                [("name", "=", "Martes"), ("product_tmpl_id.list_price", "=", 22)],
                limit=1,
            )
            product_id = product.id if product else None
        else:
            _logger.warning(
                "Contrato %s no coincide con ningún producto", contract_name
            )
            continue

        if not product_id:
            _logger.warning(
                "No se encontró un producto válido para contrato: %s", contract_name
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

        try:
            contract_line = env["contract.line"].create(
                {
                    "name": f"Línea de contrato para {contract_name} - {product_id}",
                    "contract_id": contract.id,
                    "product_id": product_id,
                    "quantity": 1,
                    "price_unit": 22,
                }
            )
            _logger.info(
                "Línea de contrato creada con ID: %s para contrato: %s",
                contract_line.id,
                contract_name,
            )
        except Exception as e:
            _logger.error("Error al crear línea de contrato: %s", str(e))

    time.sleep(2)
