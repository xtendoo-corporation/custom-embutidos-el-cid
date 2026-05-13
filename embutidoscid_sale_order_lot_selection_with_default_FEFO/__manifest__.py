{
    "name": "Sale Order Lot Selection FEFO",
    "version": "19.0.3.0.0",
    "category": "Sales Management",
    "author": "Daniel Domínguez (xtendoo)",
    "website": "https://xtendoo.es",
    "license": "AGPL-3",
    "depends": ["sale_stock", "purchase_stock", "product_expiry"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "views/sale_order_views.xml",
        "reports/sale_report_views.xml",
    ],
    "demo": ["demo/sale_demo.xml"],
    "maintainers": ["bodedra"],
    "installable": True,
}
