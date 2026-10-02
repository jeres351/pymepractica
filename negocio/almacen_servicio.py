from datos.conexion import db
from datos.modelo import Almacen, Direccion, Producto, ProductoAlmacen


class AlmacenServicio:

    def listar(self):
        return list(Almacen.select())

    def buscar(self, id_almacen):
        almacen = Almacen.get_or_none(Almacen.id_almacen == id_almacen)
        if almacen is None:
            raise ValueError("No existe un almacén con ese id")
        return almacen

    def registrar(self, id_direccion, nombre_almacen=None):
        if nombre_almacen is not None and len(nombre_almacen) > 50:
            raise ValueError("El nombre admite máximo 50 caracteres")
        if Direccion.get_or_none(Direccion.id_direccion == id_direccion) is None:
            raise ValueError("No existe una dirección con ese id")
        return Almacen.create(id_direccion=id_direccion, nombre_almacen=nombre_almacen)

    def actualizar(self, id_almacen, nombre_almacen=None, id_direccion=None):
        almacen = self.buscar(id_almacen)

        if nombre_almacen is not None:
            if len(nombre_almacen) > 50:
                raise ValueError("El nombre admite máximo 50 caracteres")
            almacen.nombre_almacen = nombre_almacen

        if id_direccion is not None:
            if Direccion.get_or_none(Direccion.id_direccion == id_direccion) is None:
                raise ValueError("No existe una dirección con ese id")
            almacen.id_direccion = id_direccion

        almacen.save()
        return almacen

    def eliminar(self, id_almacen):
        almacen = self.buscar(id_almacen)
        con_stock = ProductoAlmacen.select().where(
            ProductoAlmacen.id_almacen == id_almacen, ProductoAlmacen.stock > 0
        ).exists()
        if con_stock:
            raise ValueError("No se puede eliminar: el almacén tiene stock")
        with db.atomic():
            ProductoAlmacen.delete().where(ProductoAlmacen.id_almacen == id_almacen).execute()
            almacen.delete_instance()

    def registrar_producto(self, id_almacen, gtin):
        self.buscar(id_almacen)
        if Producto.get_or_none(Producto.gtin == gtin) is None:
            raise ValueError("No existe un producto con ese GTIN")
        ya_registrado = ProductoAlmacen.select().where(
            ProductoAlmacen.id_almacen == id_almacen,
            ProductoAlmacen.gtin_producto == gtin,
        ).exists()
        if ya_registrado:
            raise ValueError("Ese producto ya está registrado en el almacén")
        ProductoAlmacen.create(gtin_producto=gtin, id_almacen=id_almacen, stock=0)
