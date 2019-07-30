{
    "name": "Belgische steden en gemeenten (01/01/2019 Update)",
    "version": "12.0",
    "author": "",
    "category": "CRM",
    "depends": ["l10n_be", "base_address_city", "base"],
    "license": "AGPL-3",
    "summary": """All cities and states of Belgium""",
    "images": ["static/description/cover.png"],
    "data": [
        "views/res_partner.xml",
        "data/res.country.state.csv",
        "data/res.city.csv",
        "data/res.country.csv",
    ],
    "installable": True,
    "auto_install": False,
}
