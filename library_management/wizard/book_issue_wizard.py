from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class BookIssueWizardLine(models.TransientModel):
    _name = 'book.issue.wizard.line'
    _description = 'Book Issue Line'

    wizard_id = fields.Many2one('book.issue.wizard', 'Wizard', required=True, ondelete='cascade')
    book_id = fields.Many2one('library.book', 'Book', required=True)

    author_id = fields.Many2one('library.author', related='book_id.author_id', string='Author', readonly=True)
    price = fields.Integer(related='book_id.price', readonly=True)
    quantity_available = fields.Integer(related='book_id.quantity_available', readonly=True)


class BookIssue(models.TransientModel):

    _name = 'book.issue.wizard'
    _description = 'Book Issue'

    partner_id = fields.Many2one('res.partner', 'Member')
    checkout_date = fields.Date('Issue Date', default=fields.Date.today)
    line_ids = fields.One2many('book.issue.wizard.line', 'wizard_id', 'Books')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        book_id = self.env.context.get('default_book_id')
        if book_id and 'line_ids' in fields_list:
            res['line_ids'] = [(0, 0, {'book_id': book_id})]
        return res

    def action_issue_book(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError("Add at least one book to issue.")

        checkout = self.env['library.checkout'].create({'partner_id': self.partner_id.id, 'checkout_date': self.checkout_date,})

        issued_titles = []
        reserved_titles = []

        for line in self.line_ids:
            book = line.book_id

            if book.quantity_available > 0:
                self.env['library.issue'].create_issue(book, self.partner_id, checkout=checkout, issue_date=self.checkout_date)
                issued_titles.append(book.title)
            else:
                existing = self.env['library.reservation'].search([
                    ('book_id', '=', book.id),
                    ('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'waiting'),
                ], limit=1)

                if not existing:
                    queue_length = self.env['library.reservation'].search_count([
                        ('book_id', '=', book.id),
                        ('state', '=', 'waiting'),
                    ])

                    self.env['library.reservation'].create({
                        'partner_id': self.partner_id.id,
                        'book_id': book.id,
                        'sequence': queue_length + 1,
                    })
                reserved_titles.append(book.title)

        if not checkout.line_ids:
            checkout.unlink()

        if reserved_titles:
            message_parts = []
            if issued_titles:
                message_parts.append("Issued: " + ", ".join(issued_titles) + ".")
            message_parts.append("No stock available, added to reservation queue: " + ", ".join(reserved_titles) + ".")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Issue Book',
                    'message': "\n".join(message_parts),
                    'sticky': True,
                    'type': 'warning',
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }

        return {'type': 'ir.actions.act_window_close'}