# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Intecpla Custom",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "stock",  # core
        "sale_order_line_inventory",
        "hr",  # core
        "purchase_discount",  # oca/purchase-workflow
        "repair_calendar_view",  # migration from oca/manufacture v12
        "product_supplier_code_purchase",
        "account_payment_mode",  # oca/bank-payment
        "repair_validate",
        "repair_refurbish",  # migration from oca/manufacture v14
        "product_price_by_pricelist",
        "product_final_price_by_pricelist",
        "product_alternative_sale_code",
        "product_category_sale_price",
        "purchase_last_price_info",
        "product_second_name",
        "sales_team",  # core
        "invoice_supplier_last_price_info",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "category": "Warehouse",
    "data": [
        "security/ir.model.access.csv",
        "data/intecpla_scheduled_action.xml",
        "data/intecpla_custom_data.xml",
        "views/stock_picking_view.xml",
        "views/repair_order_view.xml",
        "views/sale_order_view.xml",
        "views/purchase_order_line_view.xml",
        "views/account_payment_mode_view.xml",
        "views/product_price_by_pricelist_view.xml",
        "views/product_product_view.xml",
        "views/product_template_view.xml",
        "views/product_final_price_by_pricelist_report_view.xml",
        "views/threshold_percentage_between_costs_view.xml",
        "views/purchase_order_view.xml",
        "views/product_supplierinfo_view.xml",
    ],
    "installable": True,
}
