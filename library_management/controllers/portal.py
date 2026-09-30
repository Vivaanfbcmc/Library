from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class LibraryPortal(CustomerPortal):

    @http.route('/my/library', type='http', auth='user', website=True)
    def portal_my_library(self, **kw):
        partner = request.env.user.partner_id

        issues = request.env['library.issue'].sudo().search([('partner_id', '=', partner.id),])

        returns = request.env['library.return'].sudo().search([('partner_id', '=', partner.id),])

        reservations = request.env['library.reservation'].sudo().search([('partner_id', '=', partner.id),])

        fines = request.env['account.move'].sudo().search([('partner_id', '=', partner.id),('move_type', '=', 'out_invoice'),])

        membership = request.env['library.membership'].sudo().search([('partner_id', '=', partner.id),], order='start_date desc', limit=1)

        values = {
            'issues': issues,
            'returns': returns,
            'reservations': reservations,
            'fines': fines,
            'membership': membership,
        }
        
        return request.render('library_management.portal_my_library', values)