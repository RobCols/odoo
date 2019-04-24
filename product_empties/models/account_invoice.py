from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def add_update_empty_product_line(self, product_id, quantity):
        """Add or update empty product line"""

        self.ensure_one()
        line_exist = self.invoice_line_ids.filtered(
            lambda line: line.product_id == product_id
        )
        if line_exist:
            empty_line = line_exist[:1]
            empty_line.write({"quantity": empty_line.quantity + quantity})
        else:
            name = product_id.partner_ref
            if self.type in ("in_invoice", "in_refund"):
                if product_id.description_purchase:
                    name += "\n" + product_id.description_purchase
            else:
                if product_id.description_sale:
                    name += "\n" + product_id.description_sale
            vals = {
                "name": name,
                "product_id": product_id.id,
                "quantity": quantity,
                "invoice_id": self.id,
                "origin": self.origin,
                "account_id": self.account_id.id,
                "price_unit": product_id.uom_id.id,
                "uom_id": product_id.uom_id.id,
                "invoice_line_tax_ids": self.account_id.tax_ids,
            }

            self.env["account.invoice.line"].create(vals)

    @api.multi
    def remove_update_empty_product_line(self, product_id, quantity):
        """Remove or update empty product line"""

        self.ensure_one()
        line_exist = self.invoice_line_ids.filtered(
            lambda line: line.product_id == product_id
        )
        lines_to_remove = self.env["account.invoice.line"]
        for line in line_exist:
            if quantity <= 0:
                break
            if line.quantity <= quantity:
                quantity -= line.quantity
                lines_to_remove += line
            else:
                line.write({"quantity": line.quantity - quantity})
                break
        return lines_to_remove

    def get_next_sequence(self, product_type="regular"):
        if product_type == "empty":
            seq_product_empty = list(
                self.invoice_line_ids.filtered(
                    lambda line: line.product_id.is_empty
                ).mapped("sequence")
            )
            if not seq_product_empty:
                seq_product_empty = self.get_sequence_section(product_type=product_type)
            else:
                seq_product_empty = max(seq_product_empty)
            seq_product_regular = self.get_sequence_section(product_type="regular")
            if seq_product_regular <= seq_product_empty:
                seq_product_empty = self.resequence_empty_product_lines()
                self.resequence_regular_product_lines(seq_product_empty)
            return seq_product_empty + 1
        elif product_type == "regular":
            if not self.invoice_line_ids:
                return 200
            return (max(list(self.invoice_line_ids.mapped("sequence")))) + 1
        else:
            if not self.invoice_line_ids:
                return 200
            return (max(list(self.invoice_line_ids.mapped("sequence")))) + 1

    def change_sequence(self, invoice_lines, start_seq=0):
        curr_seq = start_seq
        for line in invoice_lines:
            curr_seq += 1
            line.sequence = curr_seq
        return curr_seq

    def get_sequence_section(self, product_type="regular"):
        section = self.get_section_line(product_type=product_type)
        return section.sequence

    def create_section(self, section_name):
        vals = {
            "name": section_name,
            "display_type": "line_section",
            "sequence": 0,
            "invoice_id": self.id,
        }
        section = self.env["account.invoice.line"].create(vals)
        return section

    def get_section_line(self, product_type="regular"):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        section_ref = self.get_section_ref(product_type=product_type)
        if not section_ref:
            section_ref = "empty_product.section_name_regular_products"
        section_name = ICPSudo.get_param(section_ref)
        section = self.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
            and line.name == section_name
        )
        if not section:
            section = self.create_section(section_name=section_name)
        return section[:1]

    def get_section_ref(self, product_type="regular"):
        if product_type == "empty":
            return "empty_product.section_name_empty_products"
        elif product_type == "regular":
            return "empty_product.section_name_regular_products"
        else:
            return False

    # Section Empty
    def resequence_empty_product_lines(self):
        empty_product_lines = self.invoice_line_ids.filtered(
            lambda line: line.product_id.is_empty and not line.display_type
        )
        empty_section = self.get_section_line(product_type="empty")
        empty_section.sequence = 0
        curr_seq = self.change_sequence(
            invoice_lines=empty_product_lines, start_seq=empty_section.sequence
        )
        return curr_seq

    # Section Normal

    def resequence_regular_product_lines(self, seq_product_empty):
        regular_product_lines = self.invoice_line_ids.filtered(
            lambda line: not line.product_id.is_empty and not line.display_type
        )
        regular_section = self.get_section_line(product_type="regular")
        regular_section.sequence = seq_product_empty + 200
        curr_seq = self.change_sequence(
            invoice_lines=regular_product_lines, start_seq=regular_section.sequence
        )
        return curr_seq

    @api.multi
    def copy(self, default=None):
        self = self.with_context(do_not_add_empty_products=True)
        return super(AccountInvoice, self).copy(default)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sequence = fields.Integer(string="Sequence", default=200)

    @api.model
    def create(self, values):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(AccountInvoiceLine, self).create(values)

        product_id = values.get("product_id")
        invoice_id = self.env["account.invoice"].browse(values.get("invoice_id"))
        if product_id and not values.get("display_type") == "line_section":
            product = self.env["product.product"].browse(product_id)
            if product.is_empty:
                values["sequence"] = invoice_id.get_next_sequence(product_type="empty")
            else:
                values["sequence"] = invoice_id.get_next_sequence(
                    product_type="regular"
                )
        invoice_lines = super(AccountInvoiceLine, self).create(values)
        for invoice_line in invoice_lines:
            invoice_id = invoice_line.invoice_id
            for line in invoice_line.product_id.mapped("product_empty_ids"):
                qty = line.quantity * invoice_line.quantity
                invoice_id.add_update_empty_product_line(line.product_id, qty)
        return invoice_lines

    @api.multi
    def unlink(self):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(AccountInvoiceLine, self).unlink()

        to_remove = self
        for invoice_line in self:
            invoice_id = invoice_line.invoice_id
            for line in invoice_line.product_id.mapped("product_empty_ids"):
                qty = line.quantity * invoice_line.quantity
                to_remove |= invoice_id.remove_update_empty_product_line(
                    line.product_id, qty
                )
        return super(AccountInvoiceLine, to_remove).unlink()

    @api.multi
    def update_product_empty_line(self, product=None, quantity=None):

        self.ensure_one()

        to_remove = self.env["account.invoice.line"]
        if product and quantity:
            old_product = self.product_id
            for line in old_product.product_empty_ids:
                qty = line.quantity * self.quantity
                to_remove |= self.invoice_id.remove_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
            for line in product.product_empty_ids:
                qty = line.quantity * quantity
                self.invoice_id.add_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
        elif product:
            old_product = self.product_id
            for line in old_product.product_empty_ids:
                qty = line.quantity * self.quantity
                to_remove |= self.invoice_id.remove_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
            for line in product.product_empty_ids:
                qty = line.quantity * self.quantity
                self.invoice_id.add_update_empty_product_line(
                    product_id=line.product_id, quantity=qty
                )
        elif quantity or (not isinstance(0, bool) and quantity == 0):
            for line in self.product_id.product_empty_ids:
                if self.quantity > quantity:
                    qty = (self.quantity - quantity) * line.quantity
                    to_remove |= self.invoice_id.remove_update_empty_product_line(
                        product_id=line.product_id, quantity=qty
                    )
                elif self.quantity < quantity:
                    qty = (quantity - self.quantity) * line.quantity
                    self.invoice_id.add_update_empty_product_line(
                        product_id=line.product_id, quantity=qty
                    )
        if to_remove:
            to_remove.unlink()

    @api.multi
    def write(self, values):
        not_add_ep = self.env.context.get("do_not_add_empty_products", False)
        if not_add_ep:
            return super(AccountInvoiceLine, self).create(values)

        product = values.get("product_id", False)
        quantity = values.get("quantity", False)

        is_change_product = "product_id" in values.keys()
        is_change_quantity = "quantity" in values.keys()

        if is_change_product or is_change_quantity:
            for line in self:
                if is_change_product and not is_change_quantity:
                    line.update_product_empty_line(product=product)
                elif not is_change_product and is_change_quantity:
                    line.update_product_empty_line(quantity=quantity)
                else:
                    line.update_product_empty_line(product=product, quantity=quantity)

        return super(AccountInvoiceLine, self).write(values)

    @api.multi
    def copy(self, default=None):
        self = self.with_context(do_not_add_empty_products=True)
        return super(AccountInvoiceLine, self).copy(default)
