def deactivate_web_studio_views(env):
    target_templates = [
        'sale.report_saleorder_document',
        'stock.report_delivery_document',
        'account.report_invoice_document',
    ]
    inherit_ids = []
    for tmpl in target_templates:
        view = env.ref(tmpl, False)
        if view:
            inherit_ids.append(view.id)
    domain = [
        ('name', '=ilike', 'web_studio.report_editor_customization_diff.view%'),
        ('inherit_id', 'in', inherit_ids),
    ]
    views = env['ir.ui.view'].search(domain)
    if views:
        views.write({'active': False})
