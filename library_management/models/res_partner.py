from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership_ids = fields.One2many('library.membership', 'partner_id', 'Memberships')

    def has_active_membership(self):
        self.ensure_one()
        return bool(self.membership_ids.filtered(lambda m: m.state == 'active'))