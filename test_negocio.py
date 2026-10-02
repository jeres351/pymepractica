from datos.conexion import db
from datos.modelo import (
    Almacen, Direccion, Ingresos, Producto, ProductoAlmacen,
    Proveedor, ProveedorProducto, Salida,
)
from negocio.almacen_servicio import AlmacenServicio
from negocio.direccion_servicio import DireccionServicio
from negocio.inventario_servicio import InventarioServicio
from negocio.producto_servicio import ProductoServicio
from negocio.proveedor_servicio import ProveedorServicio

GTIN = "99999999999999"
RUT = "99999999-9"


def limpiar():
    Ingresos.delete().where(Ingresos.gtin_producto == GTIN).execute()
    Salida.delete().where(Salida.gtin_producto == GTIN).execute()
    ProductoAlmacen.delete().where(ProductoAlmacen.gtin_producto == GTIN).execute()
    ProveedorProducto.delete().where(ProveedorProducto.gtin_producto == GTIN).execute()
    Producto.delete().where(Producto.gtin == GTIN).execute()
    Proveedor.delete().where(Proveedor.rut == RUT).execute()
    Almacen.delete().where(Almacen.nombre_almacen == "Almacen de prueba").execute()
    Direccion.delete().where(Direccion.calle == "Calle de prueba").execute()


db.connect()
limpiar()

try:
    direcciones = DireccionServicio()
    proveedores = ProveedorServicio()
    almacenes = AlmacenServicio()
    productos = ProductoServicio()
    inventario = InventarioServicio()

    d = direcciones.registrar("Calle de prueba", "123", "Temuco", "Araucania")
    print("Direccion:", direcciones.obtener_direccion(d.id_direccion))

    prov = proveedores.registrar(RUT, d.id_direccion, "Proveedor prueba", "prov@prueba.cl")
    alm = almacenes.registrar(d.id_direccion, "Almacen de prueba")
    productos.registrar(GTIN, "Producto de prueba", precio_compra=1500)
    proveedores.asociar_producto(RUT, GTIN)
    print("Productos del proveedor:", len(proveedores.productos_de(RUT)))

    print("Stock tras sumar 50:", inventario.sumar_producto(GTIN, alm.id_almacen, 50, RUT, "compra inicial"))
    print("Stock tras restar 20:", inventario.restar_producto(GTIN, alm.id_almacen, 20, "venta"))
    print("Cantidad total:", inventario.consultar_cantidad(GTIN))

    try:
        inventario.restar_producto(GTIN, alm.id_almacen, 100)
    except ValueError as e:
        print("Error esperado:", e)

    try:
        inventario.sumar_producto(GTIN, alm.id_almacen, -5)
    except ValueError as e:
        print("Error esperado:", e)

    bajos = inventario.avisar_nivel_minimo(minimo=50, id_almacen=alm.id_almacen)
    print("Productos en nivel minimo:", len(bajos))

    fechas = inventario.conocer_fecha(GTIN)
    print("Ultimo ingreso:", fechas["ultimo_ingreso"])

    try:
        almacenes.eliminar(alm.id_almacen)
    except ValueError as e:
        print("Error esperado:", e)

    try:
        productos.eliminar(GTIN)
    except ValueError as e:
        print("Error esperado:", e)
finally:
    limpiar()
    print("Limpieza lista")
    db.close()
