"""Punto de entrada de la TUI. Ejecutar desde la raíz del proyecto:

    python -m presentacion.app
"""
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import ContentSwitcher, Footer, Header, OptionList, Static
from textual.widgets.option_list import Option

from datos.conexion import db
from presentacion.vistas import (
    DashboardVista, InventarioVista, Vista, vista_almacenes, vista_categorias,
    vista_direcciones, vista_productos, vista_proveedores,
)

SECCIONES = [
    ("dashboard", "  Dashboard"), ("inventario", "  Inventario"), ("productos", "  Productos"),
    ("proveedores", "  Proveedores"), ("almacenes", "  Almacenes"),
    ("categorias", "  Categorías"), ("direcciones", "  Direcciones"),
]


class PymeApp(App):
    CSS_PATH = "estilos.tcss"
    TITLE = "PymePráctica"
    SUB_TITLE = "Gestión de inventario"
    BINDINGS = [
        ("n", "accion('nuevo')", "Nuevo"),
        ("e", "accion('editar')", "Editar"),
        ("d", "accion('eliminar')", "Eliminar"),
        ("r", "refrescar", "Refrescar"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("◆ PYME", id="marca")
                yield OptionList(*[Option(nombre, id=id_) for id_, nombre in SECCIONES], id="menu")
            with ContentSwitcher(initial="dashboard", id="contenido"):
                yield DashboardVista(id="dashboard")
                yield InventarioVista(id="inventario")
                yield vista_productos(id="productos")
                yield vista_proveedores(id="proveedores")
                yield vista_almacenes(id="almacenes")
                yield vista_categorias(id="categorias")
                yield vista_direcciones(id="direcciones")
        yield Footer()

    def on_mount(self):
        self.theme = "tokyo-night"  # cámbialo con Ctrl+P → "Change theme"
        if db.is_closed():
            db.connect()
        self.query_one(OptionList).highlighted = 0
        self.call_after_refresh(self.action_refrescar_todo)

    def on_unmount(self):
        db.close()

    def _vista(self) -> Vista:
        cs = self.query_one(ContentSwitcher)
        return cs.get_child_by_id(cs.current)

    def on_option_list_option_highlighted(self, e):
        self.query_one(ContentSwitcher).current = e.option.id
        self._vista().refrescar()

    def action_accion(self, nombre):
        if len(self.screen_stack) > 1:  # hay un diálogo abierto
            return
        metodo = getattr(self._vista(), nombre, None)
        if metodo:
            metodo()

    def action_refrescar(self):
        self._vista().refrescar()
        self.notify("Datos actualizados")

    def action_refrescar_todo(self):
        for vista in self.query(Vista):
            vista.refrescar()


if __name__ == "__main__":
    PymeApp().run()
