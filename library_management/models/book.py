from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'
    _rec_name = 'title'

    title = fields.Char('Book Title', required=True)
    author_id = fields.Many2one("library.author", "Author ID")
    isbn = fields.Char('ISBN Number', required=True, readonly=True, copy=False, default='New')
    published_date = fields.Date('Published Date', default=fields.Date.today)
    price = fields.Integer('Price')
    quantity_available = fields.Integer('Quantity Available', default=0)

    is_premium = fields.Boolean('Is Premium', compute='_compute_is_premium', store=True)
    active = fields.Boolean('Active', default=True)
    book_age = fields.Integer('Book Age', compute='_compute_book_age', store=True)

    total_quantity = fields.Integer('Total Quantity', default=0)

    issue_ids = fields.One2many('library.issue', 'book_id')

    product_id = fields.Many2one('product.product', 'Product ID')

    #Odoo 19+ replaces _sql_constraints with a declarative Constraint field.
    #Postgres UNIQUE ignores NULLs, so empty ISBNs (before create() assigns one)
    #never conflict with each other - only actual duplicate ISBNs are blocked
    _isbn_unique = models.Constraint(
        'UNIQUE(isbn)',
        'ISBN Number must be unique across all books.',
    )

    @api.depends('published_date')
    def _compute_book_age(self):
        current_year = fields.Date.today().year
        for rec in self:
            if rec.published_date:
                published_year = rec.published_date.year
                rec.book_age = current_year - published_year
            else:
                rec.book_age = 0

    @api.depends('price')
    def _compute_is_premium(self):
        for rec in self:
            if rec.price > 1000:
                rec.is_premium = True
            else:
                rec.is_premium = False

    def _cron_archive_old_books(self):
        for rec in self:
            if rec.book_age > 20:
                rec.active = False

    #Using create orm method , why , becos we want the email to be send when a record is created. So we access the record at the time of creation
    #Here we use multi (for multi records)
    @api.model_create_multi
    def create(self, vals_list):

        #isbn is readonly in the UI, so it always needs to be generated here
        #server-side - readonly only blocks form input, not ORM writes.
        #The 'New' placeholder is what shows in the field before the record
        #is actually saved (Odoo doesn't call create() until then)
        for vals in vals_list:
            if not vals.get('isbn') or vals.get('isbn') == 'New':
                vals['isbn'] = self.env['ir.sequence'].next_by_code('library.book.isbn')

            #A new book starts fully in stock - quantity_available defaults
            #to whatever total_quantity was set to, unless the caller
            #explicitly passed a different quantity_available.
            if 'quantity_available' not in vals:
                vals['quantity_available'] = vals.get('total_quantity', 0)

        #Here we first create the record , since we cant reference fields like price when its in vals.list
        records = super().create(vals_list)

        #Here we first take the records present in the library_manager group by referencing external XML id to the form view of the group model in res.groups
        manager_group = self.env.ref('library_management.group_library_manager')

        #Then we use a direct method to take all the emails from each record present in the group
        #we can also run a long like "for email in emails" type but doing mapped directly takes out all emails 
        manager_emails = [email for email in manager_group.user_ids.mapped('email') if email]

        #Here we call the actual mail_template_xml and make a object of it for calling
        template = self.env.ref('library_management.mail_template_high_price_book')

        #we run the fields from the input record and check the price (not necessary for single record entry)
        for rec in records:

            #The actual condition the mail has to allow sending
            if rec.price > 2000 and manager_emails:

                #we use the base method send_mail 
                #this create a mail.mail record , (settings - technical - emails), force send directly send the email apon record creation, email_values just adds all mail to the "TO" part
                template.send_mail(rec.id, force_send=True, email_values={'email_to': ','.join(manager_emails)})

            #Auto-create the linked website product for this book (task 10).
            #is_published lives on product.template, not product.product,
            #so we write it through product_tmpl_id.
            product = self.env['product.product'].create({
                'name': rec.title,
                'list_price': rec.price,
                'sale_ok': True,
            })
            product.product_tmpl_id.is_published = rec.quantity_available > 0
            rec.product_id = product.id

        #Create method always returns a recordset
        return records

    def write(self, vals):
        result = super().write(vals)

        if 'quantity_available' in vals:
            for rec in self:
                if rec.product_id:
                    rec.product_id.product_tmpl_id.is_published = (
                        rec.quantity_available > 0
                    )

        return result

    @api.onchange('total_quantity')
    def _onchange_total_quantity(self):
        for rec in self:
            if not rec.quantity_available:
                rec.quantity_available = rec.total_quantity

    @api.constrains('quantity_available', 'total_quantity')
    def _check_quantity_bounds(self):
        for rec in self:
            if rec.quantity_available < 0:
                raise ValidationError(f"Quantity available for '{rec.title}' cannot be negative.")
            if rec.total_quantity < 0:
                raise ValidationError(f"Total quantity for '{rec.title}' cannot be negative.")
            if rec.quantity_available > rec.total_quantity:
                raise ValidationError(
                    f"Quantity available ({rec.quantity_available}) cannot exceed total quantity "
                    f"({rec.total_quantity}) for '{rec.title}'."
                )