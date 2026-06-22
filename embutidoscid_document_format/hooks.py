def deactivate_web_studio_views(env):
    view_ids = [
        2596, 2651, 2657,  # sale order
        2598, 2600, 2602, 2604, 2606, 2624, 2628, 2630,  # stock picking
    ]
    views = env['ir.ui.view'].browse(view_ids).exists()
    if views:
        views.write({'active': False})
