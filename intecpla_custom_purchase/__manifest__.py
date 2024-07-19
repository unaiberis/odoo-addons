# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Intecpla Custom",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "purchase_discount",  # oca/purchase-workflow
        "purchase_last_price_info",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/odoo-addons",
    "category": "Warehouse",
    "data": [
        "views/purchase_order_line_view.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
