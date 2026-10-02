from peewee import fn

from datos.conexion import db
from datos.modelo import (
    Almacen,
    Ingresos,
    Producto,
    ProductoAlmacen,
    Proveedor,
    Salida,
)


class InventarioServicio:

    def sumar_producto(self, gtin, id_almacen, cantidad, rut_proveedor=None, observacion=None):
        self._validar_cantidad(cantidad)
        self._validar_producto_y_almacen(gtin, id_almacen)

        if rut_proveedor is not None:
            if Proveedor.get_or_none(Proveedor.rut == rut_proveedor) is None:
                raise ValueError("No existe un proveedor con ese RUT")

        with db.atomic():
            fila = self._fila(gtin, id_almacen)
            if fila is None:
                ProductoAlmacen.create(gtin_producto=gtin, id_almacen=id_almacen, stock=cantidad)
            else:
                ProductoAlmacen.update(stock=ProductoAlmacen.stock + cantidad).where(
                    ProductoAlmacen.gtin_producto == gtin,
                    ProductoAlmacen.id_almacen == id_almacen,
                ).execute()
            Ingresos.create(
                cantidad=cantidad,
                gtin_producto=gtin,
                rut_proveedor=rut_proveedor,
                observacion=observacion,
            )

        return self.consultar_cantidad(gtin, id_almacen)

    def restar_producto(self, gtin, id_almacen, cantidad, motivo=None):
        self._validar_cantidad(cantidad)
        self._validar_producto_y_almacen(gtin, id_almacen)

        with db.atomic():
            fila = self._fila(gtin, id_almacen)
            if fila is None or fila.stock < cantidad:
                disponible = 0 if fila is None else fila.stock
                raise ValueError(f"Stock insuficiente: hay {disponible} y se piden {cantidad}")
            ProductoAlmacen.update(stock=ProductoAlmacen.stock - cantidad).where(
                ProductoAlmacen.gtin_producto == gtin,
                ProductoAlmacen.id_almacen == id_almacen,
            ).execute()
            Salida.create(cantidad=cantidad, gtin_producto=gtin, motivo=motivo)

        return self.consultar_cantidad(gtin, id_almacen)

    def consultar_cantidad(self, gtin, id_almacen=None):
        if Producto.get_or_none(Producto.gtin == gtin) is None:
            raise ValueError("No existe un producto con ese GTIN")

        consulta = ProductoAlmacen.select(
            fn.COALESCE(fn.SUM(ProductoAlmacen.stock), 0)
        ).where(ProductoAlmacen.gtin_producto == gtin)

        if id_almacen is not None:
            if Almacen.get_or_none(Almacen.id_almacen == id_almacen) is None:
                raise ValueError("No existe un almacén con ese id")
            consulta = consulta.where(ProductoAlmacen.id_almacen == id_almacen)

        return int(consulta.scalar())

    def avisar_nivel_minimo(self, minimo=10, id_almacen=None):
        consulta = ProductoAlmacen.select().where(ProductoAlmacen.stock <= minimo)
        if id_almacen is not None:
            consulta = consulta.where(ProductoAlmacen.id_almacen == id_almacen)
        return list(consulta)

    def conocer_fecha(self, gtin):
        if Producto.get_or_none(Producto.gtin == gtin) is None:
            raise ValueError("No existe un producto con ese GTIN")
        ultimo_ingreso = (
            Ingresos.select(fn.MAX(Ingresos.fecha_ingreso))
            .where(Ingresos.gtin_producto == gtin)
            .scalar()
        )
        ultima_salida = (
            Salida.select(fn.MAX(Salida.fecha_salida))
            .where(Salida.gtin_producto == gtin)
            .scalar()
        )
        return {"ultimo_ingreso": ultimo_ingreso, "ultima_salida": ultima_salida}

    def _fila(self, gtin, id_almacen):
        return ProductoAlmacen.get_or_none(
            ProductoAlmacen.gtin_producto == gtin,
            ProductoAlmacen.id_almacen == id_almacen,
        )

    def _validar_cantidad(self, cantidad):
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un número entero mayor a 0")

    def _validar_producto_y_almacen(self, gtin, id_almacen):
        if Producto.get_or_none(Producto.gtin == gtin) is None:
            raise ValueError("No existe un producto con ese GTIN")
        if Almacen.get_or_none(Almacen.id_almacen == id_almacen) is None:
            raise ValueError("No existe un almacén con ese id")
