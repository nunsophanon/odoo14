
{
    'name': 'Accounting REST API',
    'version': '14.0.1.1.0',
    'category': 'API',
    'sequence': 6,
    'summary': 'Accounting REST API',
    'license': 'OPL-1',
    'description': """

Accounting REST API

""",
    'depends': ['account', 'website_sale'],
    'data': [
        'data.xml'
    ],
    'qweb': [

    ],
    # Odoo Store Specific
    'live_test_url': 'https://www.erpcambodia.biz/',
    'images': [
        'static/description/main_screenshot.png',
    ],

    # Author
    'author': 'ERP CAMBODIA, SOHPANON',
    'website': 'https://www.erpcambodia.biz/',
    'maintainer': 'ERP CAMBODIA',

    # Technical
    'installable': True,
    'auto_install': False,
    'price': 320.0,
    'currency': 'USD',
    'support': 'erpcambo@gmail.com',
}
