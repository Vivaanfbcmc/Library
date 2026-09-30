from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class LibraryRent(http.Controller):

    @http.route('/shop/rent/<int:product_id>', type='http', auth='user', website=True)
    def rent_book(self, product_id, **kw):
        partner = request.env.user.partner_id

        book = request.env['library.book'].sudo().search(
            [('product_id', '=', product_id)], limit=1
        )
        if not book:
            return request.redirect('/shop')

        try:
            issue = request.env['library.issue'].sudo().create_issue(book, partner)
        except ValidationError as e:
            return request.render('website.404', {'status_message': str(e)})

        if not partner.has_active_membership():
            request.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Rental fee - {book.title}",
                    'quantity': 1,
                    'price_unit': book.price,
                })],
            })

        return request.render('library_management.portal_my_library', {
            'issues': request.env['library.issue'].sudo().search([('partner_id', '=', partner.id)]),
            'returns': request.env['library.return'].sudo().search([('partner_id', '=', partner.id)]),
            'reservations': request.env['library.reservation'].sudo().search([('partner_id', '=', partner.id)]),
            'fines': request.env['account.move'].sudo().search([('partner_id', '=', partner.id), ('move_type', '=', 'out_invoice')]),
            'membership': request.env['library.membership'].sudo().search([('partner_id', '=', partner.id)], order='start_date desc', limit=1),
        })