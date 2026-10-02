from decimal import Decimal

from datos.modelo import Producto


class ProductoServicio:

    def listar(self):
        return list(Producto.select())

    def registrar(self, gtin, nombre, descripcion=None, perecible=0, precio_compra=None):
        if not (gtin.isdigit() and len(gtin) == 14):
            raise ValueError("El GTIN debe tener exactamente 14 dígitos")

        if not nombre or len(nombre) > 50:
            raise ValueError("El nombre es obligatorio y admite máximo 50 caracteres")

        if precio_compra is not None and Decimal(str(precio_compra)) < 0:
            raise ValueError("El precio de compra no puede ser negativo")

        if Producto.get_or_none(Producto.gtin == gtin):
            raise ValueError("Ya existe un producto con ese GTIN")

        return Producto.create(
            gtin=gtin,
            nombre=nombre,
            descripcion_producto=descripcion,
            perecible=perecible,
            precio_compra=precio_compra,
        )
