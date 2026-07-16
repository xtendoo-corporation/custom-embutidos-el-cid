{
    'name': 'Embutidos Product',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Añade el campo ¿Producto pesado? a los productos.',
    'description': """
        Añade un campo booleano "¿Producto pesado?" en la pestaña de inventario de los productos.
    """,
    'author': 'Xtendoo',
    'website': 'https://xtendoo.es',
    'depends': ['product', 'stock'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

