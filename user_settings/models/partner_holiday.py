from odoo import api, fields, models


class PartnerHoliday(models.Model):
    _name = 'res.partner.holiday'
    _description = 'Holidays'

    holiday_date = fields.Date(string='Holiday day')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
