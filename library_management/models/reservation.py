from odoo import models, fields


class Reservation(models.Model):
    _name = 'library.reservation'
    _description = 'Book Reservation'
    _order = 'sequence, reservation_date'

    partner_id = fields.Many2one('res.partner', 'Member', required=True)
    book_id = fields.Many2one('library.book', 'Book', required=True)
    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('notified', 'Notified'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ], default='waiting', required=True)
    sequence = fields.Integer('Queue Position', default=10)
    reservation_date = fields.Date('Reservation Date', default=fields.Date.today)