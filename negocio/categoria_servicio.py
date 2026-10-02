from datos.modelo import Categoria, CategoriaProducto


class CategoriaServicio:

    def listar(self):
        return list(Categoria.select())

    def buscar(self, id_categoria):
        categoria = Categoria.get_or_none(Categoria.id_categoria == id_categoria)
        if categoria is None:
            raise ValueError("No existe una categoría con ese id")
        return categoria

    def registrar(self, nombre, descripcion=None):
        if not nombre or not nombre.strip() or len(nombre.strip()) > 35:
            raise ValueError("El nombre es obligatorio y admite máximo 35 caracteres")

        nombre = nombre.strip()

        if Categoria.get_or_none(Categoria.nombre == nombre):
            raise ValueError("Ya existe una categoría con ese nombre")

        return Categoria.create(nombre=nombre, descripcion_categoria=descripcion)

    def actualizar(self, id_categoria, nombre=None, descripcion=None):
        categoria = self.buscar(id_categoria)

        if nombre is not None:
            if not nombre.strip() or len(nombre.strip()) > 35:
                raise ValueError("El nombre es obligatorio y admite máximo 35 caracteres")
            nombre = nombre.strip()
            repetida = Categoria.get_or_none(
                (Categoria.nombre == nombre) & (Categoria.id_categoria != id_categoria)
            )
            if repetida:
                raise ValueError("Ya existe una categoría con ese nombre")
            categoria.nombre = nombre

        if descripcion is not None:
            categoria.descripcion_categoria = descripcion

        categoria.save()
        return categoria

    def eliminar(self, id_categoria):
        categoria = self.buscar(id_categoria)

        en_uso = (
            CategoriaProducto.select()
            .where(CategoriaProducto.id_categoria == id_categoria)
            .exists()
        )
        if en_uso:
            raise ValueError("No se puede eliminar: hay productos en esta categoría")

        categoria.delete_instance()
