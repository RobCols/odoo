from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    delivery_dow = fields.Selection(
        string="Delivery Day Of Week",
        selection=[
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),
        ],
    )
