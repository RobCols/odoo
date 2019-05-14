from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, ValidationError
import re


class SingupService(Component):
    _inherit = "base.rest.service"
    _name = "signup.service"
    _usage = "signup"
    _collection = "signup.services"

    def signup(self, **params):
        # sudo models
        ResUsers = self.env["res.users"].sudo()
        ResPartner = self.env["res.partner"].sudo()

        # validations
        if params["password"] != params["password2"]:
            raise ValidationError("passwords do not match")

        if ResUsers.search_count([("login", "=ilike", params["email"])]):
            raise ValidationError("user already exists")

        # create or update partner
        partner = ResPartner.search([("email", "=ilike", params["email"])])
        signup_vals = {"login": params["email"], "password": params["password"]}

        if 1 == len(partner):
            signup_vals["partner_id"] = partner.id

        if 0 == len(partner):
            signup_vals["partner_id"] = ResPartner.create(
                {
                    "email": params["email"],
                    "firstname": params["firstName"],
                    "lastname": params["lastName"],
                    "city": params["city"],
                    "zip": params["postalCode"],
                }
            ).id
        # signup user
        ResUsers.signup(signup_vals)
        return 200

    def _validator_signup(self):
        return {
            "firstName": {"type": "string", "required": True},
            "lastName": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
            "password": {"type": "string", "required": True},
            "password2": {"type": "string", "required": True},
            "city": {"type": "string", "required": True},
            "postalCode": {"type": "string", "required": True},
        }

    def _add_to_dict_if_truthy(self, origin_dict, dest_dict, key_name, dest_key_name):
        key_value = origin_dict.get(key_name, False)
        if key_value:
            dest_dict[dest_key_name] = key_value
