from odoo.addons.component.core import Component

from odoo.addons.base_rest.components.service import to_int, to_bool


class FavouritesService(Component):
    _inherit = "base.rest.service"
    _name = "favourites.service"
    _usage = "favourites"
    _collection = "user_settings.services"
    _description = """
        Favourites Services
    """

    def get(self, _id):
        """
        Get user's favourites
        """
        uid = self.env.uid
        if _id != uid:
            raise AccessError("You can only see your own favourites")
        return self._to_json(self._get(_id))

    def add(self, **params):
        """
        Add a list of favourite products to the current users's favs
        """
        uid = self.env.uid
        user = self._get(uid)
        user.partner_id.sudo().write(
            {
                "favourite_product_template_ids": [
                    (4, id, False) for id in params["productTemplateIds"]
                ]
            }
        )
        return self._to_json(self._get(uid))

    def unfavourite(self, **params):
        """
        Remove a list of favourite products from the current users's favs
        """
        uid = self.env.uid
        user = self._get(uid)
        user.partner_id.sudo().write(
            {
                "favourite_product_template_ids": [
                    (3, id, False) for id in params["productTemplateIds"]
                ]
            }
        )
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
            "productTemplateIds": {
                "type": "list",
                "required": True,
                "schema": {"type": "integer", "required": False, "empty": True},
            },
        }

    def _validator_add(self):
        return {
            "productTemplateIds": {
                "type": "list",
                "required": True,
                "schema": {"type": "integer", "required": True},
            }
        }

    def _validator_return_add(self):
        return self._validator_return_get()

    def _validator_unfavourite(self):
        return {
            "productTemplateIds": {
                "type": "list",
                "required": True,
                "schema": {"type": "integer", "required": True},
            }
        }

    def _validator_return_unfavourite(self):
        return self._validator_return_get()

    def _to_json(self, user):
        return {
            "uid": user.id,
            "partnerId": user.partner_id.id,
            "productTemplateIds": user.partner_id.favourite_product_template_ids.ids,
        }

