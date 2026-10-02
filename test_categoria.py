from datos.conexion import db
from negocio.categoria_servicio import CategoriaServicio

servicio = CategoriaServicio()
db.connect()

c = servicio.registrar("Categoria de prueba", "Descripcion inicial")
print("Registrada:", c.nombre)

try:
    servicio.registrar("Categoria de prueba")
except ValueError as e:
    print("Error esperado:", e)

c = servicio.actualizar(c.id_categoria, descripcion="Descripcion nueva")
print("Descripcion:", c.descripcion_categoria)

id_creada = c.id_categoria
servicio.eliminar(id_creada)
print("Eliminada. Categorias ahora:", len(servicio.listar()))

try:
    servicio.buscar(id_creada)
except ValueError as e:
    print("Error esperado:", e)

db.close()
