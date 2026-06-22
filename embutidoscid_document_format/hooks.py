def deactivate_web_studio_views(env):
    view_ids = [2596, 2651, 2657]
    views = env['ir.ui.view'].browse(view_ids).exists()
    if views:
        views.write({'active': False})
