from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    app_icon = fields.Binary(string="Icon")
