from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, MissingError
from odoo.addons.base_rest.components.service import to_int, to_bool


class FavouritesService(Component):
    _inherit = "base.rest.service"
    _name = "holidays.service"
    _usage = "holidays"
    _collection = "user_settings.services"
    _description = """
        Holidays Services
    """

    def get(self, _id):
        """
        Get user's holidays
        """
        uid = self.env.uid
        if _id != uid:
            raise AccessError("You can only see your own holidays")
        return self._to_json(self._get(_id))

    def add(self, **params):
        """
        Add a list of holidays to the current user's holidays
        """
        uid = self.env.uid
        user = self._get(uid)
        user.partner_id.sudo().write(
            {
                "holiday_ids": [
                    (0, False, {"partner_id": user.partner_id, "holiday_date": holiday})
                    for holiday in params["holidays"]
                ]
            }
        )
        res = self._to_json(self._get(uid))
        return res

    def remove(self, **params):
        """
        Remove a list of holidays to the current user's holidays
        """
        uid = self.env.uid
        user = self._get(uid)
        to_unlink = self.env["res.partner.holiday"].sudo().search(
            [
                ("partner_id", "=", user.partner_id.id),
                ("holiday_date", "in", params["holidays"]),
            ]
        )
        
        if not to_unlink:
            raise MissingError("holiday not found")
        
        to_unlink.unlink()

        return self._to_json(self._get(uid))

    # The following method are 'private' and should be never never NEVER call
    # from the controller.

    def _get(self, _id):
        return self.env["res.users"].browse(_id)

    # Validator
    def _validator_return_get(self):
        return {
            "uid": {"type": "integer", "required": True, "empty": False},
            "partnerId": {"type": "integer", "required": True, "empty": False},
            "holidays": {
                "type": "list",
                "required": True,
                "schema": {"type": "string", "required": False, "empty": True},
            },
        }

    def _validator_add(self):
        return {
            "holidays": {
                "type": "list",
                "required": True,
                "schema": {"type": "string", "required": True},
            }
        }

    def _validator_return_add(self):
        return self._validator_return_get()

    def _validator_remove(self):
        return {
            "holidays": {
                "type": "list",
                "required": True,
                "schema": {"type": "string", "required": True},
            }
        }

    def _validator_return_remove(self):
        return self._validator_return_get()

    def _to_json(self, user):
        user = user.sudo()
        return {
            "uid": user.id,
            "partnerId": user.partner_id.id,
            "holidays": list(map(str, user.partner_id.holiday_ids.mapped("holiday_date")))
        }
