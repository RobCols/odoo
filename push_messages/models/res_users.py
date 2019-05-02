from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    push_devices = fields.One2many(comodel_name='push.device', inverse_name='user_id', string='Push devices')
    