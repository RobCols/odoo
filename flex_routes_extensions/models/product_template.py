from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_location = fields.Char("Stocklocatie")


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_location = fields.Char(related="product_tmpl_id.stock_location")
