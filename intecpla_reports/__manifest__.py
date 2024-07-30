# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Intecpla Reports",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "intecpla_custom",
        "account_payment_partner",  # oca
        "web",
        "stock",
        "purchase_stock",
        "sale_stock",
        "account_invoice_report_due_list",  # oca
        "product_second_name",
        "sale_order_line_date",  # oca/sale-workflow
        "purchase_discount",
        "account_invoice_line_lot",
        "repair",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "category": "Warehouse",
    "data": [
        "data/paperformat_label.xml",
        "data/report_templates.xml",
        "report/invoice_report.xml",
        "report/purchase_order_report.xml",
        "report/sale_order_report.xml",
        "report/picking_report.xml",
        "report/repair_report.xml",
        "report/operation_labels_report.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "intecpla_reports/static/src/scss/layout_background.scss",
        ],
    },
}
