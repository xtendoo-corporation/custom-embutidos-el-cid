{
    "name": "Embutidos CID - Sale Custom",
    "version": "19.0.1.2.0",
    "depends": ["sale", "hr"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
    "post_init_hook": "migrate_repartidor_empleado_field",
}
