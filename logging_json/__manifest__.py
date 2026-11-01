# Copyright 2016-2021 Camptocamp SA
# Copyright 2017 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "JSON Logging",
    "summary": "Output the Odoo logs in JSON",
    "version": "19.0.1.0.0",
    "author": "Camptocamp,Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "external_dependencies": {
        "python": ["python-json-logger>=3.1"],
    },
    "installable": True,
    "post_load": "post_load",
}
