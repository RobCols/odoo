from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    original_order_reference = fields.Char("Originele order reference")