# -*- coding: utf-8 -*-
{
    'name': 'Car Rental',
    'version': '18.0.1.0.0',
    'summary': 'Manage cars, rentals, returns and invoices for car rental agencies',
    'description': """
Car Rental Management
=====================
- Car fleet with status (available, rented, maintenance)
- Rentals with automatic pricing and availability check
- Workflow, return wizard (mileage and damages), late rental alerts
- Invoicing, PDF rental contract, Agent / Manager roles
- Public JSON API of available cars
    """,
    'author': 'Amir Miled',
    'website': 'https://github.com/amirmiled/odoo-car-rental',
    'category': 'Services',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/rental_security.xml',
        'security/ir.model.access.csv',
        'data/rental_sequence.xml',
        'data/rental_cron.xml',
        'report/rental_contract_report.xml',
        'views/rental_car_views.xml',
        'views/rental_rental_views.xml',
        'views/res_partner_views.xml',
        'wizard/rental_return_wizard_views.xml'
    ],
    'application': True,
    'installable': True,
}
