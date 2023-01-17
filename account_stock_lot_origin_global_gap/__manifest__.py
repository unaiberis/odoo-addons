# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Account Stock Lot Origin Global Gap",
    "version": "16.0.1.0.0",
    "category": "Invoices & Payments",
    "license": "AGPL-3",
    "author": "https://github.com/avanzosc/odoo-addons",
    "website": "http://www.avanzosc.es",
    "depends": [
        "sale_stock",
        "stock_lot_origin_global_gap",
        "stock_picking_invoice_link",
        "mrp"
    ],
    "data": [
        "report/report_invoice.xml",
    ],
    "installable": True,
}