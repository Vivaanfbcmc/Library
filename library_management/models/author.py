from odoo import models , fields , api
from odoo.exceptions import ValidationError

class Author(models.Model):

    _name = "library.author"
    _description = "Author"


    name = fields.Char("Name", required=True)
    bio = fields.Text("Bio")
    image = fields.Binary("Image")
    book_ids = fields.One2many("library.book" , "author_id", "Books ID")
    issued_count = fields.Integer("Issued Count" ,compute="_compute_issued_count")


    @api.depends('book_ids.issue_ids')
    def _compute_issued_count(self):
        for rec in self:
            rec.issued_count = len(rec.book_ids.mapped('issue_ids'))


    def action_view_issue_book(self):
        self.ensure_one()
        return {
            'type':'ir.actions.act_window',
            'name':'Issued Books',
            'res_model':'library.issue',
            'view_mode':'list,form',
            'domain':[('book_id.author_id', '=', self.id)]

        }


    