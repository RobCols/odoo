from odoo import fields, models, api
from odoo.tools import pycompat


class ProductTemplate(models.Model):
    _inherit = "product.template"
    min_order_qty = fields.Integer("Minimum Order Quantity", default=1)
    is_empty = fields.Boolean(
        string="Is Empty",
        compute="_compute_is_empty",
        inverse="_inverse_is_empty",
        store=True,
    )
    product_empty_ids = fields.One2many(
        "product.empty", "original_product_id", "Empty Product"
    )
    unit_price = fields.Float("Price per unit")
    unit_uom = fields.Many2one("uom.uom", string="Unit for PPU")

    @api.depends("product_variant_ids", "product_variant_ids.is_empty")
    def _compute_is_empty(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.is_empty = template.product_variant_ids.is_empty
        for template in self - unique_variants:
            template.is_empty = True

    def _inverse_is_empty(self):
        for template in self:
            if len(template.product_variant_ids) != 1:
                continue
            template.product_variant_ids.is_empty = template.is_empty

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)

        for template, vals in pycompat.izip(templates, vals_list):
            related_vals = {}
            if vals.get("is_empty"):
                related_vals["is_empty"] = vals["is_empty"]
                template.write({"is_empty": vals["is_empty"]})

        return templates


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_empty = fields.Boolean(string="Is Empty")
    min_order_qty = fields.Integer(
        "Minimum Order Quantity", related="product_tmpl_id.min_order_qty"
    )
