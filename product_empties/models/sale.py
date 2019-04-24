from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    empties_price = fields.Float(
        string="Empty goods price", compute="_compute_empties_price"
    )

    products_price = fields.Float(
        string="Products price", compute="_compute_products_price"
    )

    min_quantities_reached = fields.Boolean(compute="_compute_min_quantities_reached")

    @api.depends(
        "order_line",
        "order_line.product_uom_qty",
        "order_line.product_id",
        "order_line.product_id.min_order_qty",
    )
    def _compute_min_quantities_reached(self):
        for record in self:
            record.min_quantities_reached = 0 == len(
                record.order_line.filtered(
                    lambda ol: ol.product_uom_qty < ol.product_id.min_order_qty
                )
            )

    @api.depends(
        "order_line",
        "order_line.price_total",
        "order_line.product_id",
        "order_line.product_id.is_empty",
    )
    def _compute_products_price(self):
        for record in self:
            record.products_price = sum(
                [
                    ol.price_total if not ol.product_id.is_empty else 0
                    for ol in self.order_line
                ]
            )

    @api.depends(
        "order_line",
        "order_line.price_total",
        "order_line.product_id",
        "order_line.product_id.is_empty",
    )
    def _compute_empties_price(self):
        for record in self:
            record.empties_price = sum(
                [
                    ol.price_subtotal if ol.product_id.is_empty else 0
                    for ol in self.order_line
                ]
            )

    @api.multi
    def add_update_empty_product_line(self, product_id, quantity, do_not_update=False):
        """Add or update empty line"""

        self.ensure_one()
        line_exist = self.order_line.filtered(
            lambda line: line.product_id == product_id
        )
        if line_exist and not do_not_update:
            empty_line = line_exist[:1]
            empty_line.write({"product_uom_qty": empty_line.product_uom_qty + quantity})
            order_line = empty_line
        else:
            vals = {
                "product_id": product_id.id,
                "product_uom_qty": quantity,
                "order_id": self.id,
            }
            order_line = (
                self.env["sale.order.line"]
                .with_context({"not_add_ep": True})
                .create(vals)
            )
        return order_line

    @api.multi
    def remove_update_empty_product_line(self, product_id, quantity):
        """Remove or update empty line"""

        self.ensure_one()
        line_exist = self.order_line.filtered(
            lambda line: line.product_id == product_id
        )
        lines_to_remove = self.env["sale.order.line"]
        for line in line_exist:
            if quantity <= 0:
                break
            if line.product_uom_qty <= quantity:
                quantity -= line.product_uom_qty
                lines_to_remove += line
            else:
                line.write({"product_uom_qty": line.product_uom_qty - quantity})
                break
        return lines_to_remove

    @api.model
    def create(self, values):
        # Add code here
        return super(SaleOrder, self).create(values)

    # def get_next_sequence(self, product_type='regular'):
    #     if product_type == 'empty':
    #         seq_product_empty = list(
    #             self.order_line.filtered(
    #                 lambda line:
    #                 line.product_id.is_empty
    #             ).mapped('sequence')
    #         )
    #         if not seq_product_empty:
    #             seq_product_empty = self.get_sequence_section(
    #                 product_type=product_type)
    #         else:
    #             seq_product_empty = max(seq_product_empty)
    #         seq_product_regular = self.get_sequence_section(
    #             product_type='regular')
    #         if seq_product_regular <= seq_product_empty:
    #             seq_product_empty = self.resequence_empty_product_lines()
    #             self.resequence_regular_product_lines(seq_product_empty)
    #         return seq_product_empty + 1
    #     elif product_type == 'regular':
    #         if not self.order_line:
    #             return 200
    #         return (max(list(self.order_line.mapped('sequence')))) + 1
    #     else:
    #         if not self.order_line:
    #             return 200
    #         return (max(list(self.order_line.mapped('sequence')))) + 1

    # def change_sequence(self, sol_lines, start_seq=0):
    #     curr_seq = start_seq
    #     for line in sol_lines:
    #         curr_seq += 1
    #         line.sequence = curr_seq
    #     return curr_seq

    # def get_sequence_section(self, product_type='regular'):
    #     section = self.get_section_line(product_type=product_type)
    #     return section.sequence

    # def create_section(self, section_name):
    #     vals = {
    #         'name': section_name,
    #         'display_type': 'line_section',
    #         'sequence': 0,
    #         'order_id': self.id,
    #     }
    #     section = self.env['sale.order.line'].create(vals)
    #     return section

    # def get_section_line(self, product_type='regular'):
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     section_ref = self.get_section_ref(product_type=product_type)
    #     if not section_ref:
    #         section_ref = 'empty_product.section_name_regular_products'
    #     section_name = ICPSudo.get_param(section_ref)
    #     section = self.order_line.filtered(
    #         lambda line:
    #         line.display_type == 'line_section'
    #         and line.name == section_name
    #     )
    #     if not section:
    #         section = self.create_section(section_name=section_name)
    #     return section[:1]

    # def get_section_ref(self, product_type='regular'):
    #     if product_type == 'empty':
    #         return 'empty_product.section_name_empty_products'
    #     elif product_type == 'regular':
    #         return 'empty_product.section_name_regular_products'
    #     else:
    #         return False

    # # Section Empty
    # def resequence_empty_product_lines(self):
    #     empty_product_lines = self.order_line.filtered(
    #         lambda line:
    #         line.product_id.is_empty
    #         and not line.display_type
    #     )
    #     empty_section = self.get_section_line(product_type='empty')
    #     empty_section.sequence = 0
    #     curr_seq = self.change_sequence(
    #         sol_lines=empty_product_lines,
    #         start_seq=empty_section.sequence)
    #     return curr_seq

    # # Section Normal

    # def resequence_regular_product_lines(self, seq_product_empty):
    #     regular_product_lines = self.order_line.filtered(
    #         lambda line:
    #         not line.product_id.is_empty
    #         and not line.display_type
    #     )
    #     regular_section = self.get_section_line(product_type='regular')
    #     regular_section.sequence = seq_product_empty + 200
    #     curr_seq = self.change_sequence(
    #         sol_lines=regular_product_lines,
    #         start_seq=regular_section.sequence)
    #     return curr_seq

    @api.multi
    def copy(self, default=None):
        self = self.with_context(do_not_add_empty_products=True)
        return super(SaleOrder, self).copy(default)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sequence = fields.Integer(string="Sequence", default=200)
    empties_price = fields.Float(
        string="Empties price", compute="_compute_empties_price"
    )

    @api.depends("empties_price")
    def _compute_empties_price(self):
        for record in self:
            record.empties_price = sum(
                [
                    record.product_uom_qty
                    * empty.quantity
                    * empty.product_id.list_price
                    for empty in record.product_id.product_empty_ids
                ]
            )

    @api.model
    def create(self, values):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(SaleOrderLine, self).create(values)

        product_id = values.get("product_id")
        order_id = self.env["sale.order"].browse(values.get("order_id"))
        if product_id and not values.get("display_type") == "line_section":
            product = self.env["product.product"].browse(product_id)
            # if product.is_empty:
            #     values['sequence'] = order_id.get_next_sequence(
            #         product_type='empty')
            # else:
            #     values['sequence'] = order_id.get_next_sequence(
            #         product_type='regular')
        so_lines = super(SaleOrderLine, self).create(values)
        for so_line in so_lines:
            order_id = so_line.order_id
            for line in so_line.product_id.mapped("product_empty_ids"):
                qty = line.quantity * so_line.product_uom_qty
                order_id.add_update_empty_product_line(line.product_id, qty)
        return so_lines

    @api.multi
    def unlink(self):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(SaleOrderLine, self).unlink()
        to_remove = self
        for so_line in self:
            order_id = so_line.order_id
            for line in so_line.product_id.mapped("product_empty_ids"):
                qty = line.quantity * so_line.product_uom_qty
                to_remove |= order_id.remove_update_empty_product_line(
                    line.product_id, qty
                )
        return super(SaleOrderLine, to_remove).unlink()

    @api.multi
    def update_product_empty_line(self, product=None, quantity=None):
        self.ensure_one()

        to_remove = self.env["sale.order.line"]
        if product and quantity:
            old_product = self.product_id
            for line in old_product.product_empty_ids:
                qty = line.quantity * self.product_uom_qty
                to_remove |= self.order_id.remove_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
            for line in product.product_empty_ids:
                qty = line.quantity * quantity
                self.order_id.add_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
        elif product:
            old_product = self.product_id
            for line in old_product.product_empty_ids:
                qty = line.quantity * self.product_uom_qty
                to_remove |= self.order_id.remove_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
            for line in product.product_empty_ids:
                qty = line.quantity * self.product_uom_qty
                self.order_id.add_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
        elif quantity >= 0 and not isinstance(quantity, bool):
            for line in self.product_id.product_empty_ids:
                if self.product_uom_qty > quantity:
                    qty = (self.product_uom_qty - quantity) * line.quantity
                    to_remove |= self.order_id.remove_update_empty_product_line(
                        product_id=line.product_id, quantity=qty
                    )
                elif self.product_uom_qty < quantity:
                    qty = (quantity - self.product_uom_qty) * line.quantity
                    self.order_id.add_update_empty_product_line(
                        product_id=line.product_id, quantity=qty
                    )
        if to_remove:
            to_remove.unlink()

    @api.multi
    def write(self, values):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(SaleOrderLine, self).write(values)

        for line in self:
            product = values.get("product_id", False)
            quantity = values.get("product_uom_qty", False)

            if product and isinstance(product, int):
                product = self.env["product.product"].browse(product)

            is_change_product = product and self.product_id.id != product.id
            is_change_quantity = (
                "product_uom_qty" in values.keys() and quantity != line.product_uom_qty
            )
            if not is_change_product and not is_change_quantity:
                continue
            elif is_change_product and not is_change_quantity:
                line.update_product_empty_line(product=product)
            elif not is_change_product and is_change_quantity:
                line.update_product_empty_line(quantity=quantity)
            else:
                line.update_product_empty_line(product=product, quantity=quantity)

        return super(SaleOrderLine, self).write(values)

    @api.multi
    def copy(self, default=None):
        self = self.with_context(do_not_add_empty_products=True)
        return super(SaleOrderLine, self).copy(default)
