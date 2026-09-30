from odoo import models, fields


class Checkout(models.Model):
    _name = 'library.checkout'
    _description = 'Book Checkout Batch'

    partner_id = fields.Many2one('res.partner', 'Member', required=True)
    checkout_date = fields.Date('Checkout Date', default=fields.Date.today)
    issued_by = fields.Many2one('res.users', 'Issued By', default=lambda self: self.env.user)
    line_ids = fields.One2many('library.issue', 'checkout_id', 'Issued Books')