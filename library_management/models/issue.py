from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Issue(models.Model):
    _name = 'library.issue'
    _description = 'Book Issue'

    partner_id = fields.Many2one('res.partner', 'Member')
    book_id = fields.Many2one('library.book', 'Book', ondelete="restrict")
    issue_date = fields.Date('Issue Date', default=fields.Date.today)

    due_date = fields.Date("Due Date", compute="_compute_due_date", store=True)

    checkout_id = fields.Many2one('library.checkout', 'Checkout', ondelete='cascade')
    return_ids = fields.One2many("library.return", "issue_id", "Return ID")
    calendar_event_id = fields.Many2one('calendar.event', 'Calendar Event')

    state = fields.Selection([
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], default='issued', required=True)

    @api.depends('issue_date')
    def _compute_due_date(self):
        for rec in self:
            if rec.issue_date:
                rec.due_date = rec.issue_date + timedelta(days=10)
            else:
                rec.due_date = False

    def _cron_mark_overdue(self):
        overdue_issues = self.search([('state', '=', 'issued'), ('due_date', '<', fields.Date.today())])
        overdue_issues.write({'state': 'overdue'})

    def action_view_return(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Returned Books',
            'res_model': 'library.return',
            'view_mode': 'list,form',
            'domain': [('issue_id', '=', self.id)]
        }

    def action_open_return_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Return Book',
            'res_model': 'book.return.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_issue_id': self.id},
        }

    @api.model
    def create_issue(self, book, partner, checkout=None, issue_date=None):
        """Shared entry point for issuing a single book to a member.

        Used by book.issue.wizard (backend batch checkout) and, per task 10,
        will also be called by the website Rent controller so both paths
        share one place for the stock check + issue creation.
        """
        if book.quantity_available <= 0:
            raise ValidationError(f"Cannot issue '{book.title}' - no quantity available.")

        vals = {
            'partner_id': partner.id,
            'book_id': book.id,
        }
        if checkout:
            vals['checkout_id'] = checkout.id
        if issue_date:
            vals['issue_date'] = issue_date

        record = self.create(vals)
        book.write({'quantity_available': book.quantity_available - 1})

        event = self.env['calendar.event'].create({
            'name': f"Book Due: {book.title}",
            'allday': True,
            'start_date': record.issue_date,
            'stop_date': record.due_date,
            'partner_ids': [(4, self.env.user.partner_id.id), (4, partner.id)],
        })
        record.calendar_event_id = event.id

        return record