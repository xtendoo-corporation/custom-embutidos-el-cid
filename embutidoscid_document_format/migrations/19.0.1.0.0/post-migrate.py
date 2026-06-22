def migrate(cr, version):
    cr.execute("""
        UPDATE ir_ui_view SET active=False
        WHERE name LIKE 'web_studio.report_editor_customization_diff.view.%%'
        AND inherit_id IN (
            SELECT res_id FROM ir_model_data
            WHERE model = 'ir.ui.view'
            AND ((module = 'sale' AND name = 'report_saleorder_document')
                 OR (module = 'stock' AND name = 'report_delivery_document')
                 OR (module = 'account' AND name = 'report_invoice_document'))
        )
    """)
