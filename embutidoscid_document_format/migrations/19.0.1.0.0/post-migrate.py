def migrate(cr, version):
    cr.execute("UPDATE ir_ui_view SET active=False WHERE id IN (2596,2651,2657)")
