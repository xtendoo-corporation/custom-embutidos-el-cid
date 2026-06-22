import logging
from lxml import etree

_logger = logging.getLogger(__name__)

_OLD_FIELD_CANDIDATES = [
    "x_studio_repartidor_empleado",
    "x_studio_repartidor",
]

_STOCK_REF_FIELD = "stock_reference_ids"

def _find_old_field(env):
    for name in _OLD_FIELD_CANDIDATES:
        field = env["ir.model.fields"].search([
            ("model", "=", "sale.order"),
            ("name", "=", name),
        ], limit=1)
        if field:
            _logger.info("Campo studio encontrado: %s", name)
            return name
    return None

def _strip_field_from_views(env, field_name, label=""):
    """Remove all references to field_name from views' arch_db."""
    views = env["ir.ui.view"].search([("arch_db", "ilike", field_name)])
    if not views:
        return
    for view in views:
        try:
            old_arch = (view.arch_db or "").encode("utf-8")
            root = etree.fromstring(old_arch)
            changed = False
            for elem in list(root.iter()):
                if elem.tag == "field" and elem.get("name") == field_name:
                    parent = elem.getparent()
                    if parent is not None:
                        parent.remove(elem)
                        changed = True
                elif elem.tag == "xpath":
                    expr = (elem.get("expr") or "")
                    if field_name in expr:
                        parent = elem.getparent()
                        if parent is not None:
                            parent.remove(elem)
                            changed = True
                elif elem.tag == "attribute":
                    if field_name in (elem.get("name") or "") or field_name in (elem.text or ""):
                        parent = elem.getparent()
                        if parent is not None:
                            parent.remove(elem)
                            changed = True
            if changed:
                new_arch = etree.tostring(root, encoding="unicode")
                view.write({"arch_db": new_arch})
                _logger.info(
                    "Eliminado campo %s de vista %s (id: %s)",
                    field_name, view.name, view.id,
                )
        except Exception as e:
            _logger.warning(
                "Error al procesar vista %s (id: %s): %s", view.name, view.id, e,
            )


def migrate_repartidor_empleado_field(env):
    old_name = _find_old_field(env)
    if old_name:
        # 1. Migrate data via SQL
        env.cr.execute(
            "SELECT id, %s FROM sale_order WHERE %s IS NOT NULL AND repartidor_empleado_id IS NULL"
            % (old_name, old_name)
        )
        rows = env.cr.fetchall()
        migrated = 0
        for row_id, old_val in rows:
            try:
                env.cr.execute(
                    "UPDATE sale_order SET repartidor_empleado_id = %s WHERE id = %s",
                    [int(old_val), int(row_id)],
                )
                migrated += 1
            except (ValueError, TypeError):
                pass
        _logger.info("Migrados %d pedidos con repartidor (campo: %s)", migrated, old_name)

        # 2. Strip old studio field from all views
        _strip_field_from_views(env, old_name)

    # 3. Strip stock_reference_ids from all views (leftover from studio customization)
    _strip_field_from_views(env, _STOCK_REF_FIELD)

    # 4. Do NOT delete the old field (other fields may depend on it).
    #    It will stay in ir.model.fields but won't appear in any view
    #    since we already removed it from the view arch above.
