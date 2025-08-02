# -*- coding: utf-8 -*-
{
    'name': "QuickDesk",

    'summary': "Simple and efficient help desk system for managing support tickets",

    'description': """
QuickDesk

The purpose of QuickDesk is to provide a simple, easy-to-use help desk solution
where users can raise support tickets, and support staff can manage and resolve
them efficiently. The system aims to streamline communication between users
and support teams without unnecessary complexity.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Customer Relationship Management',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],

    'demo': [
        # 'demo/demo.xml',
    ],

    'application': True,
    'installable': True,
}
