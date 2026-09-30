from odoo import models, fields, api

class Return(models.Model):
    _name = 'library.return'
    _description = 'Book Return'

    partner_id = fields.Many2one('res.partner', 'Member')
    book_id = fields.Many2one('library.book', 'Book')
    return_date = fields.Date('Return Date')

    issue_id = fields.Many2one('library.issue', required=True)