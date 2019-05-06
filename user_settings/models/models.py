from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    delivery_notification_sms = fields.Boolean(
        "Delivery notification via SMS", default=False
    )
    delivery_notification_push = fields.Boolean(
        "Delivery notification via push", default=True
    )

    invoice_notification_email = fields.Boolean(
        "Invoice notification via email", default=False
    )
    invoice_notification_push = fields.Boolean(
        "Invoice notification via push", default=True
    )

    no_more_deliveries = fields.Boolean("No more deliveries required", default=False)
