# Changelog

## [19.0.3.0.0] - 2026-06-04

### Añadido

#### Campos de Lote y Fecha de Caducidad en Líneas de Entrada

- **Modelo stock.move**: Añadido campo `expiration_date` relacionado con `restrict_lot_id` para mostrar la fecha de caducidad del lote en los movimientos de stock.

- **Modelo stock.move.line**: Añadido campo `expiration_date` relacionado con `lot_id` para mostrar la fecha de caducidad en las líneas detalladas de operaciones.

- **Vistas actualizadas**:
  - Vista de formulario de picking (`stock.picking`): Añadido campo de fecha de caducidad después del campo de lotes en la lista de movimientos.
  - Vista de operaciones (`stock.move.line`): Añadido campo de fecha de caducidad en ambas vistas de árbol de operaciones (estándar y detallada).
  - Campo `lot_id` y `lot_name` renombrados a "Lote" en las vistas de operaciones.

#### Campos de Lote y Fecha de Caducidad en Líneas de Factura

- **Modelo account.move.line**:
  - Añadido campo `lot_id` con propagación automática desde movimientos de stock
  - Añadido campo `expiration_date` relacionado con el lote
  - **Propagación automática del lote**: El lote se obtiene automáticamente desde:
    - Líneas de pedido de venta (`sale_line_ids`) → movimientos de stock
    - Líneas de pedido de compra (`purchase_line_id`) → movimientos de stock

- **Lógica de búsqueda del lote**:
  1. Primero busca el lote directo en la línea de pedido (si existe `lot_id` en `sale.order.line` o `purchase.order.line`)
  2. Luego busca en el campo `restrict_lot_id` de los movimientos de stock completados (`state='done'`)
  3. Finalmente busca en las líneas de movimiento (`move_line_ids.lot_id`)
  4. El campo sigue siendo editable para cambios manuales si es necesario

- **Vista de factura**:
  - Añadidos campos de lote y fecha de caducidad en las líneas de factura
  - Solo visibles para productos con seguimiento por lotes
  - Solo visibles para usuarios con permisos de lotes/números de serie

### Características

- Los campos de fecha de caducidad se muestran automáticamente cuando se selecciona un lote
- Los campos solo son visibles para usuarios con permisos de lotes/números de serie (`stock.group_production_lot`)
- Los campos de fecha de caducidad son de solo lectura y se actualizan automáticamente según el lote seleccionado
- **El lote se propaga automáticamente desde las entregas/recepciones a las facturas**
- Compatible con productos que tienen seguimiento por lotes o números de serie
- Funciona tanto para facturas de cliente como de proveedor

### Ubicación de los cambios

- `models/stock_move.py`: Campo expiration_date en movimientos de stock
- `models/stock_move_line.py`: Campo expiration_date en líneas detalladas de operaciones
- `models/account_move_line.py`: Campos lot_id y expiration_date en líneas de factura con propagación automática
- `views/stock_picking_views.xml`: Vistas actualizadas para mostrar los nuevos campos en operaciones
- `views/account_move_views.xml`: Vista de facturas con campos de lote y caducidad

### Uso

Una vez actualizado el módulo:

#### En Recepciones/Entregas:
1. Ir a Inventario > Operaciones > Recepciones (o cualquier tipo de operación de stock)
2. En las líneas de productos con seguimiento por lotes:
   - El campo "Lote" ahora estará visible
   - Justo después aparecerá el campo "Caducidad" mostrando la fecha de caducidad del lote seleccionado
3. En las operaciones detalladas (botón "Detailed Operations"):
   - También aparecerán ambos campos: lote y fecha de caducidad

#### En Facturas:
1. Crear o abrir una factura de cliente/proveedor
2. En las líneas de productos con seguimiento por lotes:
   - El campo "Lote" aparecerá automáticamente rellenado con el lote usado en la entrega/recepción
   - El campo "Caducidad" mostrará la fecha de caducidad del lote
3. Los campos son editables si necesitas cambiarlos manualmente

### Notas técnicas

- El campo `expiration_date` es un campo relacionado (`related`) que obtiene su valor directamente del lote
- Se utiliza `store=True` para mejorar el rendimiento en búsquedas e informes
- El campo es de solo lectura (`readonly=True`) para mantener la integridad de los datos
- El campo `lot_id` en facturas es un campo computed pero editable (`readonly=False`)
- La propagación del lote respeta lotes asignados manualmente
- Se actualiza automáticamente al cambiar el producto

