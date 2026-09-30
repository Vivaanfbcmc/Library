{
    'name': 'Library Management',
    'version': '19.0.1.0.0',
    'summary': 'Library Management System',
    'description': 'Module for managing Library and book',
    'author': 'Vivaan',
    'category': 'Library',

    'depends': ['base', 'mail', 'calendar', 'account', 'portal', 'website', 'website_sale'],

    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'security/portal_security.xml',

        'data/cron.xml',
        'data/mail_template.xml',
        
        'report/library_book_report.xml',

        'views/book_issue_wizard_view.xml',
        'views/book_return_wizard_view.xml',
        'views/book_views.xml',
        'views/author_views.xml',
        'views/issue_views.xml',
        'views/return_views.xml',
        'views/checkout_views.xml',
        'views/reservation_views.xml',
        'views/membership_views.xml',
        'views/portal_template.xml',
        'views/website_template.xml',
        'views/menu_views.xml',

        
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}