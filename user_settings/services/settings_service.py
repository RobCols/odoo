from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, ValidationError
import re


class SettingsService(Component):
    _inherit = "base.rest.service"
    _name = "settings.service"
    _usage = "settings"
    _collection = "user_settings.services"

    def get(self, _id):
        uid = self.env.uid
        if _id != uid:
            raise AccessError("You can only edit your own user settings")
        user = self.env["res.users"].sudo().browse(uid)
        partner = user.partner_id

        delivery_notifications = []
        if partner.delivery_notification_sms:
            delivery_notifications.append("sms")
        if partner.delivery_notification_push:
            delivery_notifications.append("app")

        invoice_notifications = []

        if partner.invoice_notification_email:
            invoice_notifications.append("email")
        if partner.invoice_notification_push:
            invoice_notifications.append("app")

        result = {
            "firstName": partner.firstname,
            "lastName": partner.lastname,
            "streetAndNr": partner.street,
            "postalCode": partner.zip,
            "city": partner.city,
            "email": partner.email,
            "deliveryPreference": partner.comment,
            "deliveryNotifications": delivery_notifications,
            "deliveryInvoiceNotifications": invoice_notifications,
            "noFurtherDeliveries": partner.no_more_deliveries,
        }

        if not partner.parent_id:
            return result

        result["company"] = {
            "name": partner.parent_id.name,
            "vatNr": partner.parent_id.vat,
        }

        return result

    def update(self, _id, **params):
        uid = self.env.uid
        if _id != uid:
            raise AccessError("You can only edit your own user settings")
        user = self.env["res.users"].sudo().browse(uid)
        partner = user.partner_id

        partner_vals = {}
        company_vals = {}

        self._add_to_dict_if_truthy(params, partner_vals, "firstName", "firstname")
        self._add_to_dict_if_truthy(params, partner_vals, "lastName", "lastname")
        self._add_to_dict_if_truthy(params, partner_vals, "streetAndNr", "street")
        self._add_to_dict_if_truthy(params, partner_vals, "postalCode", "zip")
        self._add_to_dict_if_truthy(params, partner_vals, "city", "city")
        self._add_to_dict_if_truthy(params, partner_vals, "email", "email")
        self._add_to_dict_if_truthy(
            params, partner_vals, "noFurtherDeliveries", "no_more_deliveries"
        )

        if "deliveryNotifications" in params:
            partner_vals["delivery_notification_sms"] = False
            partner_vals["delivery_notification_push"] = False
            if "sms" in params["deliveryNotifications"]:
                partner_vals["delivery_notification_sms"] = True
            if "app" in params["deliveryNotifications"]:
                partner_vals["delivery_notification_push"] = True

        if "deliveryInvoiceNotifications" in params:
            partner_vals["invoice_notification_email"] = False
            partner_vals["invoice_notification_push"] = False
            if "email" in params["deliveryInvoiceNotifications"]:
                partner_vals["invoice_notification_email"] = True
            if "app" in params["deliveryInvoiceNotifications"]:
                partner_vals["invoice_notification_push"] = True

        company = self.env["res.partner"].sudo()
        if "company" in params:
            if params["company"].get("vatNr", False):
                company_vals["vat"] = params["company"]["vatNr"]
                company = company.search(
                    [
                        (
                            "sanitized_vat",
                            "=",
                            re.sub(r"\W+", "", company_vals["vat"]).upper(),
                        ),
                        ("is_company", "=", True),
                    ]
                )
            if params["company"].get("name", False):
                company_vals["name"] = params["company"]["name"]
            if not len(company):
                if "name" not in company_vals:
                    company_vals["name"] = partner.name + " COMPANY"
                company_vals["company_type"] = "company"
                company = self.env["res.partner"].sudo().create(company_vals)
            elif len(company) == 1:
                company.write(company_vals)
            else:
                raise ValidationError(
                    "Multiple companies found for this VAT Number :("
                )

        if len(company):
            partner_vals["parent_id"] = company.id

        partner.write(partner_vals)

        return self.get(_id)

    # Validator
    def _validator_get(self):
        return {}

    def _validator_return_get(self):
        return {
            "firstName": {"type": "string"},
            "lastName": {"type": "string"},
            "streetAndNr": {"type": "string"},
            "postalCode": {"type": "string"},
            "city": {"type": "string"},
            "email": {"type": "string"},
            "company": {
                "type": "dict",
                "schema": {"name": {"type": "string"}, "vatNr": {"type": "string"}},
            },
            "deliveryNotifications": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "default": "sms",
                    "allowed": ["sms", "app"],
                },
            },
            "deliveryInvoiceNotifications": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "default": "email",
                    "allowed": ["email", "app"],
                },
            },
            "noFurtherDeliveries": {"type": "boolean", "coerce": to_bool},
        }

    def _validator_update(self):
        return {
            "firstName": {"type": "string"},
            "lastName": {"type": "string"},
            "streetAndNr": {"type": "string"},
            "postalCode": {"type": "string"},
            "city": {"type": "string"},
            "email": {"type": "string"},
            "company": {
                "type": "dict",
                "schema": {"name": {"type": "string"}, "vatNr": {"type": "string"}},
            },
            "deliveryNotifications": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "default": "sms",
                    "allowed": ["sms", "app"],
                },
            },
            "deliveryInvoiceNotifications": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "default": "email",
                    "allowed": ["email", "app"],
                },
            },
            "noFurtherDeliveries": {"type": "boolean", "coerce": to_bool},
        }

    def _add_to_dict_if_truthy(self, origin_dict, dest_dict, key_name, dest_key_name):
        key_value = origin_dict.get(key_name, False)
        if key_value:
            dest_dict[dest_key_name] = key_value
