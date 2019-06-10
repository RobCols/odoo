from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Many2one


class PushDevice(models.Model):
    _name = "push.device"
    _description = "Push Device"
    _rec_name = "registration_token"

    registration_token = fields.Char(string="Registration Token", required=True)
    user_id = fields.Many2one("res.users")

    @api.constrains("registration_token")
    def _check_registration_token(self):
        check_duplicate = self.search(
            [("registration_token", "=", self.registration_token)]
        )
        if check_duplicate - self:
            raise ValidationError(_("Registration Token should be unique."))
