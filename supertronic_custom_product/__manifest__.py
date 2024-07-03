{
    "name": "Custom Supertronic Module",
    "version": "14.0.1.0.0",
    "category": "Custom",
    "summary": "Custom module for Supertronic with additional fields",
    "website": "http://github.com/avanzosc/odoo-addons",
    "author": "AvanzOSC",
    "depends": [
        "mrp",
        "project",
        "project_mrp",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/project_task_views.xml",
        "views/sale_order_line_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
