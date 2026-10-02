from datos.modelo import Almacen, Direccion, Proveedor


class DireccionServicio:

    def listar(self):
        return list(Direccion.select())

    def buscar(self, id_direccion):
        direccion = Direccion.get_or_none(Direccion.id_direccion == id_direccion)
        if direccion is None:
            raise ValueError("No existe una dirección con ese id")
        return direccion

    def registrar(self, calle, numero_lugar, comuna, region):
        self._validar("calle", calle, 100)
        self._validar("número", numero_lugar, 30)
        self._validar("comuna", comuna, 100)
        self._validar("región", region, 100)
        return Direccion.create(
            calle=calle.strip(),
            numero_lugar=numero_lugar.strip(),
            comuna=comuna.strip(),
            region=region.strip(),
        )

    def actualizar(self, id_direccion, calle=None, numero_lugar=None, comuna=None, region=None):
        direccion = self.buscar(id_direccion)
        cambios = {
            "calle": (calle, 100),
            "numero_lugar": (numero_lugar, 30),
            "comuna": (comuna, 100),
            "region": (region, 100),
        }
        for campo, (valor, maximo) in cambios.items():
            if valor is not None:
                self._validar(campo, valor, maximo)
                setattr(direccion, campo, valor.strip())
        direccion.save()
        return direccion

    def eliminar(self, id_direccion):
        direccion = self.buscar(id_direccion)
        if Almacen.select().where(Almacen.id_direccion == id_direccion).exists():
            raise ValueError("No se puede eliminar: hay un almacén con esta dirección")
        if Proveedor.select().where(Proveedor.id_direccion == id_direccion).exists():
            raise ValueError("No se puede eliminar: hay un proveedor con esta dirección")
        direccion.delete_instance()

    def obtener_direccion(self, id_direccion):
        d = self.buscar(id_direccion)
        return f"{d.calle} {d.numero_lugar}, {d.comuna}, {d.region}"

    def _validar(self, campo, valor, maximo):
        if not valor or not valor.strip() or len(valor.strip()) > maximo:
            raise ValueError(f"El campo {campo} es obligatorio y admite máximo {maximo} caracteres")
