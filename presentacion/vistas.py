"""Vistas y diálogos de la capa de presentación (Textual)."""
from decimal import Decimal

from peewee import PeeweeException, fn
from rich.text import Text
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from datos.modelo import Almacen, Producto, ProductoAlmacen, Proveedor
from negocio.almacen_servicio import AlmacenServicio
from negocio.categoria_servicio import CategoriaServicio
from negocio.direccion_servicio import DireccionServicio
from negocio.inventario_servicio import InventarioServicio
from negocio.producto_servicio import ProductoServicio
from negocio.proveedor_servicio import ProveedorServicio

MINIMO = 10
ERRORES = (ValueError, ArithmeticError, PeeweeException)

inv = InventarioServicio()
direcciones = DireccionServicio()


# ---------- utilidades ----------
def opt(s):
    return s.strip() or None


def entero(s, campo):
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"{campo} debe ser un número entero") from None


def dinero(s):
    if not s:
        return None
    try:
        return Decimal(s.replace(",", "."))
    except ArithmeticError:
        raise ValueError("El precio debe ser un número") from None


def pesos(v):
    return "—" if v is None else f"${v:,.0f}".replace(",", ".")


def fecha(v):
    return str(v)[:16] if v else "—"


def clave_de(tabla):
    if tabla.row_count == 0:
        return None
    return tabla.coordinate_to_cell_key(tabla.cursor_coordinate).row_key.value


# ---------- diálogos ----------
class FormModal(ModalScreen[bool]):
    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, titulo, campos, accion, valores=None, bloqueados=()):
        super().__init__()
        self.titulo, self.campos, self.accion = titulo, campos, accion
        self.valores, self.bloqueados = valores or {}, bloqueados

    def compose(self):
        with Vertical(id="dialogo"):
            yield Label(self.titulo, classes="titulo")
            for clave, etiqueta in self.campos:
                v = self.valores.get(clave)
                yield Label(etiqueta)
                yield Input(
                    value="" if v is None else str(v),
                    id=f"f_{clave}",
                    disabled=clave in self.bloqueados,
                )
            yield Static("", id="error")
            with Horizontal(id="botones"):
                yield Button("Cancelar", id="cancelar")
                yield Button("Guardar", id="guardar", variant="success")

    def on_mount(self):
        for campo in self.query(Input):
            if not campo.disabled:
                campo.focus()
                break

    def _enviar(self):
        datos = {c: self.query_one(f"#f_{c}", Input).value.strip() for c, _ in self.campos}
        try:
            self.accion(datos)
        except ERRORES as e:  # el diálogo sigue abierto para corregir
            self.query_one("#error", Static).update(f"[b red]✗[/b red] {e}")
            return
        self.dismiss(True)

    def on_button_pressed(self, e):
        self._enviar() if e.button.id == "guardar" else self.dismiss(False)

    def on_input_submitted(self, _):
        self._enviar()

    def action_cancelar(self):
        self.dismiss(False)


class ConfirmModal(ModalScreen[bool]):
    BINDINGS = [("escape", "no", "No")]

    def __init__(self, mensaje):
        super().__init__()
        self.mensaje = mensaje

    def compose(self):
        with Vertical(id="dialogo"):
            yield Label(self.mensaje)
            with Horizontal(id="botones"):
                yield Button("Cancelar", id="no")
                yield Button("Eliminar", id="si", variant="error")

    def on_button_pressed(self, e):
        self.dismiss(e.button.id == "si")

    def action_no(self):
        self.dismiss(False)


# ---------- vistas ----------
class Vista(Vertical):
    def refrescar(self):
        pass


class DashboardVista(Vista):
    TARJETAS = (("t_prod", "Productos"), ("t_prov", "Proveedores"),
                ("t_alm", "Almacenes"), ("t_stock", "Unidades en stock"))

    def compose(self):
        yield Label("Resumen", classes="titulo")
        with Horizontal(classes="tarjetas"):
            for id_, _ in self.TARJETAS:
                yield Static(id=id_, classes="tarjeta")
        yield Label(f"Productos en nivel mínimo (≤ {MINIMO} unidades)", classes="titulo")
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        self.query_one(DataTable).add_columns("GTIN", "Producto", "Almacén", "Stock", "Último ingreso")

    def refrescar(self):
        stock = ProductoAlmacen.select(fn.COALESCE(fn.SUM(ProductoAlmacen.stock), 0)).scalar()
        datos = {"t_prod": Producto.select().count(), "t_prov": Proveedor.select().count(),
                 "t_alm": Almacen.select().count(), "t_stock": int(stock)}
        for id_, nombre in self.TARJETAS:
            self.query_one(f"#{id_}", Static).update(f"[b]{datos[id_]}[/b]\n{nombre}")
        tabla = self.query_one(DataTable)
        tabla.clear()
        for pa in inv.avisar_nivel_minimo(MINIMO):
            gtin = pa.gtin_producto_id
            tabla.add_row(
                gtin, pa.gtin_producto.nombre,
                pa.id_almacen.nombre_almacen or f"#{pa.id_almacen_id}",
                Text(str(pa.stock), style="bold red"),
                fecha(inv.conocer_fecha(gtin)["ultimo_ingreso"]),
            )


class CrudVista(Vista):
    def __init__(self, titulo, columnas, filas, campos, crear, actualizar, borrar,
                 valores, bloqueados=(), **kw):
        super().__init__(**kw)
        self.titulo, self.columnas, self.filas = titulo, columnas, filas
        self.campos, self.crear, self.actualizar = campos, crear, actualizar
        self.borrar, self.valores, self.bloqueados = borrar, valores, bloqueados

    def compose(self):
        yield Label(self.titulo, classes="titulo")
        with Horizontal(classes="barra"):
            yield Button("Nuevo (n)", id="nuevo", variant="success")
            yield Button("Editar (e)", id="editar", variant="primary")
            yield Button("Eliminar (d)", id="eliminar", variant="error")
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        self.query_one(DataTable).add_columns(*self.columnas)

    def refrescar(self):
        tabla = self.query_one(DataTable)
        tabla.clear()
        for clave, celdas in self.filas():
            tabla.add_row(*celdas, key=str(clave))

    def _tras(self, ok, mensaje):
        if ok:
            self.refrescar()
            self.app.notify(mensaje)

    def nuevo(self):
        self.app.push_screen(
            FormModal(f"Nuevo · {self.titulo}", self.campos, self.crear),
            lambda ok: self._tras(ok, "Registro creado"))

    def editar(self):
        clave = clave_de(self.query_one(DataTable))
        if clave is None:
            return self.app.notify("Selecciona una fila", severity="warning")
        self.app.push_screen(
            FormModal(f"Editar · {self.titulo}", self.campos,
                      lambda d: self.actualizar(clave, d), self.valores(clave), self.bloqueados),
            lambda ok: self._tras(ok, "Registro actualizado"))

    def eliminar(self):
        clave = clave_de(self.query_one(DataTable))
        if clave is None:
            return self.app.notify("Selecciona una fila", severity="warning")

        def confirmado(ok):
            if not ok:
                return
            try:
                self.borrar(clave)
            except ERRORES as e:
                return self.app.notify(str(e), title="No se pudo eliminar", severity="error", timeout=7)
            self.refrescar()
            self.app.notify("Registro eliminado")

        self.app.push_screen(ConfirmModal(f"¿Eliminar «{clave}»? Esta acción no se puede deshacer."), confirmado)

    def on_button_pressed(self, e):
        getattr(self, e.button.id)()


class InventarioVista(Vista):
    def compose(self):
        yield Label("Inventario por almacén", classes="titulo")
        with Horizontal(classes="barra"):
            yield Button("Ingreso (n)", id="ingreso", variant="success")
            yield Button("Salida", id="salida", variant="warning")
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        self.query_one(DataTable).add_columns("GTIN", "Producto", "Almacén", "Stock")

    def refrescar(self):
        tabla = self.query_one(DataTable)
        tabla.clear()
        for pa in ProductoAlmacen.select():
            color = "bold red" if pa.stock <= MINIMO else "green"
            tabla.add_row(
                pa.gtin_producto_id, pa.gtin_producto.nombre,
                pa.id_almacen.nombre_almacen or f"#{pa.id_almacen_id}",
                Text(str(pa.stock), style=color),
                key=f"{pa.gtin_producto_id}|{pa.id_almacen_id}",
            )

    def _abrir(self, titulo, campos, accion):
        clave = clave_de(self.query_one(DataTable))
        previo = dict(zip(("gtin", "almacen"), clave.split("|"))) if clave else {}
        self.app.push_screen(FormModal(titulo, campos, accion, previo),
                             lambda ok: ok and self.refrescar())

    def ingreso(self):
        def accion(d):
            nuevo = inv.sumar_producto(d["gtin"], entero(d["almacen"], "El almacén"),
                                       entero(d["cantidad"], "La cantidad"), opt(d["rut"]), opt(d["obs"]))
            self.app.notify(f"Ingreso registrado. Stock en el almacén: {nuevo}")
        self._abrir("Ingreso de stock",
                    [("gtin", "GTIN del producto"), ("almacen", "ID del almacén"), ("cantidad", "Cantidad"),
                     ("rut", "RUT del proveedor (opcional)"), ("obs", "Observación (opcional)")], accion)

    def salida(self):
        def accion(d):
            nuevo = inv.restar_producto(d["gtin"], entero(d["almacen"], "El almacén"),
                                        entero(d["cantidad"], "La cantidad"), opt(d["motivo"]))
            self.app.notify(f"Salida registrada. Stock en el almacén: {nuevo}")
        self._abrir("Salida de stock",
                    [("gtin", "GTIN del producto"), ("almacen", "ID del almacén"),
                     ("cantidad", "Cantidad"), ("motivo", "Motivo (opcional)")], accion)

    nuevo = ingreso

    def on_button_pressed(self, e):
        getattr(self, e.button.id)()


# ---------- fábricas de CRUD ----------
def vista_productos(**kw):
    s = ProductoServicio()
    return CrudVista(
        "Productos", ["GTIN", "Nombre", "Perecible", "Precio compra"],
        lambda: [(p.gtin, [p.gtin, p.nombre, "Sí" if p.perecible else "No", pesos(p.precio_compra)])
                 for p in s.listar()],
        [("gtin", "GTIN (14 dígitos)"), ("nombre", "Nombre"), ("descripcion", "Descripción"),
         ("perecible", "Perecible (0 = no, 1 = sí)"), ("precio", "Precio de compra")],
        lambda d: s.registrar(d["gtin"], d["nombre"], opt(d["descripcion"]),
                              entero(d["perecible"] or "0", "Perecible"), dinero(d["precio"])),
        lambda k, d: s.actualizar(k, d["nombre"], d["descripcion"],
                                  entero(d["perecible"], "Perecible") if d["perecible"] else None,
                                  dinero(d["precio"])),
        s.eliminar,
        lambda k: (lambda p: {"gtin": p.gtin, "nombre": p.nombre, "descripcion": p.descripcion_producto,
                              "perecible": p.perecible, "precio": p.precio_compra})(s.buscar(k)),
        bloqueados=("gtin",), **kw)


def vista_proveedores(**kw):
    s = ProveedorServicio()
    return CrudVista(
        "Proveedores", ["RUT", "Nombre", "Correo", "Dirección"],
        lambda: [(p.rut, [p.rut, p.nombre or "—", p.correo or "—",
                          direcciones.obtener_direccion(p.id_direccion_id)]) for p in s.listar()],
        [("rut", "RUT"), ("nombre", "Nombre"), ("correo", "Correo"), ("dir", "ID de dirección")],
        lambda d: s.registrar(d["rut"], entero(d["dir"], "La dirección"), opt(d["nombre"]), opt(d["correo"])),
        lambda k, d: s.actualizar(k, opt(d["nombre"]), opt(d["correo"]),
                                  entero(d["dir"], "La dirección") if d["dir"] else None),
        s.eliminar,
        lambda k: (lambda p: {"rut": p.rut, "nombre": p.nombre, "correo": p.correo,
                              "dir": p.id_direccion_id})(s.buscar(k)),
        bloqueados=("rut",), **kw)


def vista_almacenes(**kw):
    s = AlmacenServicio()
    return CrudVista(
        "Almacenes", ["ID", "Nombre", "Dirección"],
        lambda: [(a.id_almacen, [a.id_almacen, a.nombre_almacen or "—",
                                 direcciones.obtener_direccion(a.id_direccion_id)]) for a in s.listar()],
        [("nombre", "Nombre"), ("dir", "ID de dirección")],
        lambda d: s.registrar(entero(d["dir"], "La dirección"), opt(d["nombre"])),
        lambda k, d: s.actualizar(int(k), opt(d["nombre"]),
                                  entero(d["dir"], "La dirección") if d["dir"] else None),
        lambda k: s.eliminar(int(k)),
        lambda k: (lambda a: {"nombre": a.nombre_almacen, "dir": a.id_direccion_id})(s.buscar(int(k))),
        **kw)


def vista_direcciones(**kw):
    s = DireccionServicio()
    campos = [("calle", "Calle"), ("numero", "Número"), ("comuna", "Comuna"), ("region", "Región")]
    return CrudVista(
        "Direcciones", ["ID", "Calle", "Número", "Comuna", "Región"],
        lambda: [(d.id_direccion, [d.id_direccion, d.calle, d.numero_lugar, d.comuna, d.region])
                 for d in s.listar()],
        campos,
        lambda d: s.registrar(d["calle"], d["numero"], d["comuna"], d["region"]),
        lambda k, d: s.actualizar(int(k), opt(d["calle"]), opt(d["numero"]), opt(d["comuna"]), opt(d["region"])),
        lambda k: s.eliminar(int(k)),
        lambda k: (lambda d: {"calle": d.calle, "numero": d.numero_lugar,
                              "comuna": d.comuna, "region": d.region})(s.buscar(int(k))),
        **kw)


def vista_categorias(**kw):
    s = CategoriaServicio()
    return CrudVista(
        "Categorías", ["ID", "Nombre", "Descripción"],
        lambda: [(c.id_categoria, [c.id_categoria, c.nombre, c.descripcion_categoria or "—"])
                 for c in s.listar()],
        [("nombre", "Nombre"), ("descripcion", "Descripción")],
        lambda d: s.registrar(d["nombre"], opt(d["descripcion"])),
        lambda k, d: s.actualizar(int(k), opt(d["nombre"]), opt(d["descripcion"])),
        lambda k: s.eliminar(int(k)),
        lambda k: (lambda c: {"nombre": c.nombre, "descripcion": c.descripcion_categoria})(s.buscar(int(k))),
        **kw)
