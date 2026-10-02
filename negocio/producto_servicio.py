from decimal import Decimal

from peewee import IntegrityError

from datos.modelo import CategoriaProducto, Producto, ProductoAlmacen


class ProductoServicio:

    def listar(self):
        return list(Producto.select())

    def buscar(self, gtin):
        producto = Producto.get_or_none(Producto.gtin == gtin)
        if producto is None:
            raise ValueError("No existe un producto con ese GTIN")
        return producto

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

    def actualizar(self, gtin, nombre=None, descripcion=None, perecible=None, precio_compra=None):
        producto = self.buscar(gtin)

        if nombre is not None:
            if not nombre or len(nombre) > 50:
                raise ValueError("El nombre es obligatorio y admite máximo 50 caracteres")
            producto.nombre = nombre

        if descripcion is not None:
            producto.descripcion_producto = descripcion

        if perecible is not None:
            producto.perecible = perecible

        if precio_compra is not None:
            if Decimal(str(precio_compra)) < 0:
                raise ValueError("El precio de compra no puede ser negativo")
            producto.precio_compra = precio_compra

        producto.save()
        return producto

    def eliminar(self, gtin):
        producto = self.buscar(gtin)

        con_stock = (
            ProductoAlmacen.select()
            .where(ProductoAlmacen.gtin_producto == gtin, ProductoAlmacen.stock > 0)
            .exists()
        )
        if con_stock:
            raise ValueError("No se puede eliminar: el producto tiene stock en algún almacén")

        try:
            CategoriaProducto.delete().where(CategoriaProducto.gtin_producto == gtin).execute()
            producto.delete_instance()
        except IntegrityError:
            raise ValueError("No se puede eliminar: el producto tiene registros asociados")
