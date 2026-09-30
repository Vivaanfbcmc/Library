from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class Membership(models.Model):
    _name = 'library.membership'
    _description = 'Library Membership'

    partner_id = fields.Many2one('res.partner', 'Member', required=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], default='active', required=True)

    start_date = fields.Date('Start Date', default=fields.Date.today, required=True)

    duration_months = fields.Selection([
        ('1', '1 Month'),
        ('3', '3 Months'),
        ('6', '6 Months'),
        ('12', '12 Months'),
    ], default='1', required=True)

    end_date = fields.Date('End Date', compute='_compute_end_date', store=True, readonly=True)
    monthly_fee = fields.Float('Monthly Fee')

    next_invoice_date = fields.Date('Next Invoice Date', default=fields.Date.today)

    @api.depends('start_date', 'duration_months')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date and rec.duration_months:
                rec.end_date = rec.start_date + relativedelta(months=int(rec.duration_months))
            else:
                rec.end_date = False

    def action_cancel_membership(self):
        for rec in self:
            rec.write({
                'state': 'cancelled',
                'end_date': fields.Date.today(),
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._create_membership_invoice()
            rec.next_invoice_date = rec.next_invoice_date + relativedelta(months=1)
        return records

    def _create_membership_invoice(self):
        self.ensure_one()
        return self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f"Library membership fee - {self.partner_id.name}",
                'quantity': 1,
                'price_unit': self.monthly_fee,
            })],
        })

    def _cron_bill_memberships(self):
        today = fields.Date.today()
        memberships = self.search([
            ('state', '=', 'active'),
            ('next_invoice_date', '<=', today),
        ])

        for membership in memberships:
            if membership.end_date and membership.end_date <= today:
                membership.state = 'expired'
                continue

            membership._create_membership_invoice()
            membership.next_invoice_date = membership.next_invoice_date + relativedelta(months=1)