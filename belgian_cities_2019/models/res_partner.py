from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    country_id = fields.Many2one(default=lambda self: self.env.ref("base.be"))
