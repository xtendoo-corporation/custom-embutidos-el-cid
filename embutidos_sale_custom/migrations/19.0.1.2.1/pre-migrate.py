def migrate(cr, version):
    cr.execute(
        "ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS show_sale_buttons BOOLEAN DEFAULT TRUE"
    )
    cr.execute(
        "UPDATE res_partner SET show_sale_buttons = TRUE WHERE show_sale_buttons IS NULL"
    )

