{
    "name": "Custom Sale Order Report",
    "version": "1.0",
    "license": "AGPL-3",
    "summary": "Customize Sale Order Report in Odoo 16",
    "description": "Module to customize the Sale Order report in Odoo version 16.",
    "author": "Avanzosc",
    "category": "Sales",
    "depends": ["sale", "sale_management"],
    "data": [
        "views/sale_order_report_inherit.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
