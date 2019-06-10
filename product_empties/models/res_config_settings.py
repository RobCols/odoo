from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    empty_section_name = fields.Char(string="Section Name(Empty Products)")
    regular_section_name = fields.Char(string="Section Name(Regular Products)")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        empty_section_name = ICPSudo.get_param(
            "empty_product.section_name_empty_products"
        )
        regular_section_name = ICPSudo.get_param(
            "empty_product.section_name_regular_products"
        )
        res.update(
            empty_section_name=empty_section_name,
            regular_section_name=regular_section_name,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "empty_product.section_name_empty_products", self.empty_section_name
        )
        ICPSudo.set_param(
            "empty_product.section_name_regular_products", self.regular_section_name
        )
