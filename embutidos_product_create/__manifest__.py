{
    "name": "Embutidos - Control creación/edición de productos",
    "version": "1.0.0",
    "summary": "Restringe la creación/modificación de productos por usuario y pide una clave",
    "category": "Custom",
    "author": "xtendoo",
    "website": "",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
        "wizard/product_key_wizard_views.xml",
        "views/product_views.xml",
        # Also load the client QWeb template as data so it's registered in ir.ui.view
        # and available to the client regardless of asset bundling mode.
        "views/qweb_product_key_dialog_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "embutidos_product_create/static/src/js/components/product_key_dialog.js",
            "embutidos_product_create/static/src/js/product_key_guard.esm.js"
        ],
        "web.assets_qweb": [
            "embutidos_product_create/static/src/xml/product_key_dialog.xml"
        ],

    },
    "installable": True,
    "application": False,
}

