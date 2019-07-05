# -*- coding: utf-8 -*-
{
    "name": "settings_service",
    "summary": """user_settings
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Abstractive BVBA",
    "website": "http://www.abstractive.be",
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base_rest",
        "component",
        "base_vat_sanitized",
        "partner_firstname",
        "flex_courier_rounds",
    ],
    "data": ["security/ir.model.access.csv"],
}
