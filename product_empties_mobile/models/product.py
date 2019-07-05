from odoo import fields, models, api
from odoo.tools import pycompat


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_manual_empty = fields.Boolean(
        string="Is Manual Empty",
        compute="_compute_is_manual_empty",
        inverse="_inverse_is_manual_empty",
        store=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.is_manual_empty")
    def _compute_is_manual_empty(self):
        unique_variants = self.sudo().filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.is_manual_empty = template.product_variant_ids.is_manual_empty
        for template in self - unique_variants:
            variant_manual_empty = template.product_variant_ids.mapped(
                "is_manual_empty"
            )
            if any(list(variant_manual_empty)):
                template.is_manual_empty = True
            else:
                template.is_manual_empty = False

    def _inverse_is_manual_empty(self):
        for template in self.sudo():
            if len(template.product_variant_ids) != 1:
                continue
            template.product_variant_ids.is_manual_empty = template.is_manual_empty

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)

        for template, vals in pycompat.izip(templates, vals_list):
            related_vals = {}
            if vals.get("is_manual_empty"):
                related_vals["is_manual_empty"] = vals["is_manual_empty"]
                template.write(related_vals)

        return templates


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_manual_empty = fields.Boolean(string="Is Manual Empty")
