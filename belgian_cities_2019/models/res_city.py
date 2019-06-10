from odoo import api, fields, models


class ResCity(models.Model):
    _inherit = "res.city"
    _order = 'zipcode'

    @api.multi
    def name_get(self):
        for record in self:
            yield (record.id, f"{record.zipcode} - {record.name}")

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        return list(self.search(
            ["|", ("name", operator, name), ("zipcode", '=ilike', name + '%')]
        ).name_get())
