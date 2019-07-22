from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    crate_equivalence = fields.Float("Crate equivalence")


class ProductProduct(models.Model):
    _inherit = "product.product"

    crate_equivalence = fields.Float(
        "Crate equivalence", related="product_tmpl_id.crate_equivalence"
    )
