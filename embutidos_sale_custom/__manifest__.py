{
    "name": "Embutidos CID - Sale Custom",
    "version": "19.0.1.2.2",
    "depends": ["sale", "hr", "sale_stock", "embutidoscid_sale_order_picking_all_done"],
    "data": [
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
    "post_init_hook": "migrate_repartidor_empleado_field",
}
