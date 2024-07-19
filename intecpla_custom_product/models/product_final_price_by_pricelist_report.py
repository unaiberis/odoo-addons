# Copyright 2020 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductFinalPriceByPricelist(models.Model):
    _inherit = "product.final.price.by.pricelist.report"

    description_sale_es = fields.Char(
        string="Name of the product in sales (Spanish)",
        copy=False,
    )
    description_sale_en = fields.Char(
        string="Name of the product in sales (English)",
        copy=False,
    )
    description_sale_cat = fields.Char(
        string="Name of the product in sales (Catalan)",
        copy=False,
    )

    _depends = {
        "product.location.exploded": [
            "product_final_id",
            "position",
            "product_id",
        ],
        "product.price.by.pricelist": [
            "product_id",
            "pricelist_id",
            "price_unit",
            "description_sale_es",
            "description_sale_en",
            "description_sale_cat",
        ],
    }

    def _select(self):
        select_str = super()._select()
        if "description_sale_es" not in select_str:
            select_str += ", product_price.description_sale_es as description_sale_es"
        if "description_sale_en" not in select_str:
            select_str += ", product_price.description_sale_en as description_sale_en"
        if "description_sale_cat" not in select_str:
            select_str += ", product_price.description_sale_cat as description_sale_cat"
        return select_str

    def _group_by(self):
        group_by_str = super()._group_by()
        if "description_sale_es" not in group_by_str:
            group_by_str += ", product_price.description_sale_es"
        if "description_sale_en" not in group_by_str:
            group_by_str += ", product_price.description_sale_en"
        if "description_sale_cat" not in group_by_str:
            group_by_str += ", product_price.description_sale_cat"
        return group_by_str
