from odoo import models, fields, api
from odoo.exceptions import ValidationError

FINE_PERCENTAGE = 0.02  # 2% of book price per day late


class BookReturn(models.TransientModel):

    _name = 'book.return.wizard'
    _description = 'Book Return'

    issue_id = fields.Many2one('library.issue', required=True, domain="[('state','in',['issued','overdue'])]")
    partner_id = fields.Many2one('res.partner', 'Member', related='issue_id.partner_id', readonly=True)
    book_id = fields.Many2one('library.book', 'Book', related='issue_id.book_id', readonly=True)

    return_date = fields.Date('Return Date', default=fields.Date.today)

    def action_return_book(self):
        self.ensure_one()
        book = self.issue_id.book_id

        if book.quantity_available + 1 > book.total_quantity:
            raise ValidationError(
                f"Cannot return '{book.title}' - this would put available stock above the total quantity owned ({book.total_quantity})."
            )

        if self.return_date > self.issue_id.due_date:
            days_late = (self.return_date - self.issue_id.due_date).days
            fine_amount = book.price * FINE_PERCENTAGE * days_late

            self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Late return fee - {book.title}",
                    'quantity': 1,
                    'price_unit': fine_amount,
                })],
            })

        self.env['library.return'].create({
            'partner_id': self.partner_id.id,
            'book_id': book.id,
            'issue_id': self.issue_id.id,
            'return_date': self.return_date,
        })

        self.issue_id.write({'state': 'returned'})
        book.write({'quantity_available': book.quantity_available + 1})

        if self.issue_id.calendar_event_id:
            self.issue_id.calendar_event_id.unlink()

        reservation = self.env['library.reservation'].search([
            ('book_id', '=', book.id),
            ('state', '=', 'waiting'),
        ], order='sequence', limit=1)

        if reservation:
            self.env['library.issue'].create_issue(book, reservation.partner_id)
            reservation.unlink()

            remaining = self.env['library.reservation'].search([
                ('book_id', '=', book.id),
                ('state', '=', 'waiting'),
            ], order='sequence')
            for position, rec in enumerate(remaining, start=1):
                rec.sequence = position