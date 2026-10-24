# Library Management (Odoo 19 CE)

A custom Odoo 19 Community Edition module that runs a small library end to end. It handles books and authors, issuing and returning, reservation queues, late fines, memberships, and a customer portal. Books are also listed on the website shop so members can rent them online.

![Library dashboard](docs/screenshots/dashboard.png)
<!-- Screenshot: Library app home / books list -->

## Features

**Books and authors**
- Books with title, author, price, published date, total quantity and available quantity
- ISBN is generated automatically (`ISBN0001`, `ISBN0002`...) and must be unique
- Books priced above 1000 are flagged as premium
- Book age is computed from the published date
- Adding a book priced above 2000 emails all Library Managers
- Stock checks make sure available quantity never goes negative or above total quantity
- Authors have a bio, image, list of books and a smart button to see all issued books

![Book form](docs/screenshots/book-form.png)
<!-- Screenshot: Book form view -->

![Author form](docs/screenshots/author-form.png)
<!-- Screenshot: Author form with the issued books smart button -->

**Issuing books**
- Batch checkout wizard: pick a member and add several books in one go
- Due date is set to 10 days after the issue date
- Each issue creates an all day calendar event for the due period
- If a book has no stock left, the member is added to its reservation queue instead

![Issue wizard](docs/screenshots/issue-wizard.png)
<!-- Screenshot: Book issue wizard with multiple book lines -->

**Returning books**
- Return wizard on each issue
- Late returns create a customer invoice for the fine (2% of the book price per day late)
- Stock goes back up and the calendar event is removed
- If someone is waiting in the reservation queue, the book is issued to the first person automatically and the queue positions shift up

![Return wizard](docs/screenshots/return-wizard.png)
<!-- Screenshot: Return wizard / late fee invoice -->

**Reservations**
- Queue per book, ordered by position and reservation date
- States: Waiting, Notified, Fulfilled, Cancelled

![Reservations](docs/screenshots/reservations.png)
<!-- Screenshot: Reservations list -->

**Memberships**
- Duration of 1, 3, 6 or 12 months with a monthly fee
- An invoice is created when the membership is created, then one every month
- Expires automatically at the end date, and can be cancelled manually

![Membership form](docs/screenshots/membership.png)
<!-- Screenshot: Membership form and generated invoice -->

**Website and portal**
- Every book creates a linked product that is published on the shop while stock is available
- A Rent button shows up on the product page for books in stock
- Members without an active membership get a rental fee invoice when they rent
- `/my/library` portal page shows issues, returns, reservations, fines and membership
- Confirming a sale order for a book product reduces its stock

![Shop rent button](docs/screenshots/website-rent.png)
<!-- Screenshot: Product page with the Rent button -->

![Portal page](docs/screenshots/portal.png)
<!-- Screenshot: /my/library portal page -->

**Reports**
- Book List PDF report, available from the Print menu on the book list

![Book list report](docs/screenshots/report.png)
<!-- Screenshot: Printed book list PDF -->

## Scheduled actions

| Name | Runs | What it does |
|------|------|--------------|
| Archive Old Books | Daily | Archives books older than 20 years |
| Overdue Status | Daily | Marks issued books past their due date as overdue |
| Book Due Reminder | Daily | Emails members 2 days before the due date |
| Library Membership Billing | Daily | Creates monthly membership invoices and expires finished memberships |

## Access rights

| Group | Access |
|-------|--------|
| Library User | Read only on books, authors, issues, returns, checkouts, reservations and memberships. Can use the issue and return wizards |
| Library Manager | Full access to everything (includes Library User) |

## Dependencies

`base`, `mail`, `calendar`, `account`, `portal`, `website`, `website_sale`

## Installation

1. Copy the `library_management` folder into your Odoo addons path.
2. Restart the Odoo server.
3. Turn on developer mode and go to Apps, then click Update Apps List.
4. Search for "Library Management" and click Install.
5. Give your users the Library User or Library Manager group.

Or from the command line:

```bash
./odoo-bin -c odoo.conf -d your_db -i library_management
```

To upgrade after changes:

```bash
./odoo-bin -c odoo.conf -d your_db -u library_management
```

## Module structure

```
library_management/
├── controllers/   # portal page and website rent route
├── data/          # cron jobs, ISBN sequence, mail templates
├── models/        # book, author, issue, return, checkout, reservation, membership
├── report/        # book list PDF
├── security/      # groups, access rights, portal rules
├── views/         # backend views, menus, portal and website templates
└── wizard/        # issue and return wizards
```

## Models

| Model | Purpose |
|-------|---------|
| `library.book` | Book with stock, ISBN and linked shop product |
| `library.author` | Author details and their books |
| `library.checkout` | Batch of books issued together |
| `library.issue` | One book issued to one member |
| `library.return` | Return record for an issue |
| `library.reservation` | Waiting queue entry for a book |
| `library.membership` | Member subscription with recurring invoices |

## Usage flow

1. Create authors and books (set the total quantity).
2. Open Issues and use the issue wizard to check out books to a member.
3. When the book comes back, open the issue and click return.
4. Check Reservations for anyone waiting and Memberships for billing.

## Author

Vivaan Patange

## License

LGPL-3
