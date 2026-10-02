from datos.conexion import db
from datos.modelo import Producto
from negocio.producto_servicio import ProductoServicio

servicio = ProductoServicio()
db.connect()

# 1. Un producto válido: debe guardarse
p = servicio.registrar("12345678901234", "Producto de prueba", precio_compra=1500)
print("Registrado:", p.nombre)

# 2. El mismo GTIN otra vez: debe fallar
try:
    servicio.registrar("12345678901234", "Repetido")
except ValueError as e:
    print("Error esperado:", e)

# 3. Un GTIN corto: debe fallar
try:
    servicio.registrar("123", "GTIN corto")
except ValueError as e:
    print("Error esperado:", e)

# Limpieza: borra el producto de prueba
Producto.delete_by_id("12345678901234")
print("Productos al final:", len(servicio.listar()))

db.close()
