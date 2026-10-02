from peewee import IntegrityError

from datos.conexion import db
from datos.modelo import Direccion, Producto, Proveedor, ProveedorProducto


class ProveedorServicio:

    def listar(self):
        return list(Proveedor.select())

    def buscar(self, rut):
        proveedor = Proveedor.get_or_none(Proveedor.rut == rut)
        if proveedor is None:
            raise ValueError("No existe un proveedor con ese RUT")
        return proveedor

    def registrar(self, rut, id_direccion, nombre=None, correo=None):
        if not rut or not rut.strip() or len(rut.strip()) > 15:
            raise ValueError("El RUT es obligatorio y admite máximo 15 caracteres")
        rut = rut.strip()

        if nombre is not None and len(nombre) > 30:
            raise ValueError("El nombre admite máximo 30 caracteres")

        if correo is not None and ("@" not in correo or len(correo) > 50):
            raise ValueError("El correo no es válido (debe tener @ y máximo 50 caracteres)")

        if Direccion.get_or_none(Direccion.id_direccion == id_direccion) is None:
            raise ValueError("No existe una dirección con ese id")

        if Proveedor.get_or_none(Proveedor.rut == rut):
            raise ValueError("Ya existe un proveedor con ese RUT")

        return Proveedor.create(
            rut=rut, id_direccion=id_direccion, nombre=nombre, correo=correo
        )

    def actualizar(self, rut, nombre=None, correo=None, id_direccion=None):
        proveedor = self.buscar(rut)

        if nombre is not None:
            if len(nombre) > 30:
                raise ValueError("El nombre admite máximo 30 caracteres")
            proveedor.nombre = nombre

        if correo is not None:
            if "@" not in correo or len(correo) > 50:
                raise ValueError("El correo no es válido (debe tener @ y máximo 50 caracteres)")
            proveedor.correo = correo

        if id_direccion is not None:
            if Direccion.get_or_none(Direccion.id_direccion == id_direccion) is None:
                raise ValueError("No existe una dirección con ese id")
            proveedor.id_direccion = id_direccion

        proveedor.save()
        return proveedor

    def eliminar(self, rut):
        proveedor = self.buscar(rut)
        try:
            with db.atomic():
                ProveedorProducto.delete().where(ProveedorProducto.rut_proveedor == rut).execute()
                proveedor.delete_instance()
        except IntegrityError:
            raise ValueError("No se puede eliminar: el proveedor tiene ingresos registrados")

    def asociar_producto(self, rut, gtin):
        self.buscar(rut)
        if Producto.get_or_none(Producto.gtin == gtin) is None:
            raise ValueError("No existe un producto con ese GTIN")
        ya_asociado = ProveedorProducto.select().where(
            ProveedorProducto.rut_proveedor == rut,
            ProveedorProducto.gtin_producto == gtin,
        ).exists()
        if ya_asociado:
            raise ValueError("Ese proveedor ya entrega ese producto")
        ProveedorProducto.create(rut_proveedor=rut, gtin_producto=gtin)

    def desasociar_producto(self, rut, gtin):
        self.buscar(rut)
        borradas = ProveedorProducto.delete().where(
            ProveedorProducto.rut_proveedor == rut,
            ProveedorProducto.gtin_producto == gtin,
        ).execute()
        if borradas == 0:
            raise ValueError("Ese proveedor no entrega ese producto")

    def productos_de(self, rut):
        self.buscar(rut)
        return list(
            Producto.select()
            .join(ProveedorProducto, on=(ProveedorProducto.gtin_producto == Producto.gtin))
            .where(ProveedorProducto.rut_proveedor == rut)
        )
