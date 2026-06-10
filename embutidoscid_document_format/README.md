# Embutidos CID - Document Format

## Descripción

Módulo que personaliza el formato de impresión de los albaranes de entrega para incluir:

### Información de Trazabilidad
- Número de lote
- Fecha de caducidad del lote
- Datos completos del producto

### Información Económica
- Precio unitario de venta
- Descuentos aplicados (%)
- Subtotal por línea
- Subtotal sin impuestos
- Impuestos totales
- Total general

### Información del Pedido
- Referencia del pedido de venta
- Referencia del cliente
- Condiciones de pago

## Características

- Se integra automáticamente con los pedidos de venta vinculados al albarán
- Calcula automáticamente los precios en proporción a la cantidad entregada
- Solo muestra datos económicos en albaranes vinculados a pedidos de venta
- Compatible con el módulo de trazabilidad por lotes y fechas de caducidad

## Dependencias

- `sale_stock`: Integración de ventas con inventario
- `product_expiry`: Gestión de fechas de caducidad

## Instalación

1. Copiar el módulo en la carpeta de addons
2. Actualizar lista de aplicaciones
3. Instalar "Embutidos CID - Document Format"

## Uso

Una vez instalado, todos los albaranes de entrega vinculados a pedidos de venta mostrarán automáticamente la información económica y de trazabilidad completa.

## Autor

- **Daniel Domínguez** - [Xtendoo](https://xtendoo.es)

## Licencia

AGPL-3

