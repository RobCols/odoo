from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    original_client_id = fields.Char(string="Original Client ID")
    onboarding_condition = fields.Char(string="Onboarding Condition")
    customer_status = fields.Selection(
        selection=[
            ("periodical", "Ordering periodically"),
            ("no", "No longer ordering"),
            ("first", "Ordering for the first times"),
            ("occasional", "Ordering occasionally"),
        ]
    )
