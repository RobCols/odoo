from odoo import fields, models, api


class PushDeviceMixin(models.AbstractModel):
    _name = "push.device.mixin"
    _description = "Push Device Mixin"

    device_ids = fields.One2many(
        "push.device",
        "res_id",
        string="Devices",
        compute="_compute_get_device",
        inverse="_inverse_set_device",
    )

    @api.multi
    def _compute_get_device(self):
        push_device = self.env["push.device"]
        for record in self:
            result = push_device.search(
                [("res_id", "=", record.id), ("res_model", "=", record._name)]
            )
            record.device_ids = result.ids

    @api.multi
    def _inverse_set_device(self):
        for record in self:
            devices = record.device_ids.filtered(
                lambda d: not d.res_model or not d.res_id
            )
            old_devices = record.device_ids.search(
                [["res_id", "=", record.id], ["res_model", "=", self._name]]
            )
            push_devices = []
            for device in devices:
                push_devices.append(
                    {
                        "registration_token": device.registration_token,
                        "res_id": record.id,
                        "res_model": self._name,
                    }
                )
            for device in push_devices:
                record.device_ids.create(device)
            if old_devices:
                to_remove = old_devices - record.device_ids
                if to_remove:
                    to_remove.unlink()
