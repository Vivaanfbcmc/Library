from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            for line in order.order_line:
                book = self.env['library.book'].sudo().search(
                    [('product_id', '=', line.product_id.id)], limit=1
                )
                if not book:
                    continue

                qty = int(line.product_uom_qty)
                book.write({
                    'quantity_available': max(book.quantity_available - qty, 0),
                    'total_quantity': max(book.total_quantity - qty, 0),
                })

        return res