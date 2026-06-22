def migrate(cr, version):
    cr.execute("UPDATE ir_ui_view SET active=False WHERE id IN (2596,2651,2657,2598,2600,2602,2604,2606,2624,2628,2630)")
