{
    "name": "Embutidos CID - Purchase Custom",
    "version": "19.0.1.0.0",
    "category": "Purchases",
    "summary": "Fecha de caducidad editable en compras y recepción automática con lotes",
    "author": "Daniel Domínguez (xtendoo)",
    "website": "https://xtendoo.es",
    "license": "LGPL-3",
    "depends": [
        "purchase_stock",
        "product_expiry",
        "embutidoscid_sale_order_lot_selection_with_default_FEFO",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
