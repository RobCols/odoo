{
    'name': 'Flex Sale flows',
    'version': '12',
    'summary': 'Bevat de nodige code voor de correcte verkoopsflows',
    'category': '',
    'author': 'Abstractive BVBA',
    'maintainer': 'Abstractive BVBA',
    'website': 'https://abstractive.be',
    'license': 'OPL-1',
    'depends': [
        'base', 'sale', 'account'
    ],
    'data': [
        'data/delivery_notes.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
