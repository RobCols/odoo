from odoo import fields, models


class ProductEmpty(models.Model):

    _name = "product.empty"
    _description = "product empty"

    original_product_id = fields.Many2one(
        "product.template", string="Original Product Id"
    )
    quantity = fields.Float(string="Quantity", required=True)
    product_id = fields.Many2one(
        "product.product", domain=[("is_empty", "=", True)], string="Product"
    )
