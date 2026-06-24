from nicegui import ui, app
from database import ejecutar_consulta
from auth import obtener_preventista_id, obtener_usuario_actual
from pedidos import agregar_al_carrito, obtener_carrito

def mostrar_mapa():
    """Crea un mapa Leaflet con marcadores de clientes asignados al preventista."""
    usuario = obtener_usuario_actual()
    if not usuario:
        ui.notify("Debe iniciar sesión", type="warning")
        return
    preventista_id = usuario.get("preventista_id")
    if not preventista_id and not usuario.get("rol") == "admin":
        ui.notify("Usuario no asociado a un preventista", type="warning")
        return
    # Obtener clientes (si es admin, todos; si no, solo los asignados)
    if usuario["rol"] == "admin":
        clientes = ejecutar_consulta("SELECT id, razon_social, latitud, longitud FROM clientes WHERE latitud IS NOT NULL AND longitud IS NOT NULL")
    else:
        clientes = ejecutar_consulta(
            "SELECT id, razon_social, latitud, longitud FROM clientes WHERE preventista_id = ? AND latitud IS NOT NULL AND longitud IS NOT NULL",
            (preventista_id,)
        )
    if not clientes:
        ui.label("No hay clientes con coordenadas cargadas.").classes("text-grey")
        return
    # Generar HTML/JavaScript para el mapa
    markers_js = []
    for c in clientes:
        markers_js.append(f"""
            L.marker([{c['latitud']}, {c['longitud']}]).addTo(map)
            .bindPopup(`
                <b>{c['razon_social']}</b><br>
                <button onclick="window.dispatchEvent(new CustomEvent('abrir_catalogo', {{detail: {{cliente_id: {c['id']}}}}})">Ver catálogo</button>
            `);
        """)
    js_code = """
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map" style="height: 500px;"></div>
    <script>
        var map = L.map('map').setView([-38.4161, -63.6167], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(map);
        """ + "\n".join(markers_js) + """
        // Escuchar evento personalizado
        window.addEventListener('abrir_catalogo', (e) => {
            const cliente_id = e.detail.cliente_id;
            // Llamar a NiceGUI mediante un fetch o un enlace especial
            fetch('/_nicegui/open_client_catalog?cliente_id=' + cliente_id);
        });
    </script>
    """
    ui.html(js_code)

# Endpoint para abrir el catálogo desde el mapa (NiceGUI puede tener rutas)
@ui.page('/abrir_catalogo/{cliente_id}')
async def abrir_catalogo(cliente_id: int):
    from nicegui import ui
    usuario = obtener_usuario_actual()
    if not usuario:
        ui.label("No autorizado")
        return
    cliente = ejecutar_consulta("SELECT id, razon_social FROM clientes WHERE id = ?", (cliente_id,))
    if not cliente:
        ui.label("Cliente no encontrado")
        return
    cliente = cliente[0]
    with ui.dialog() as dialog, ui.card():
        ui.label(f"Catálogo para {cliente['razon_social']}").classes("text-h6")
        # Búsqueda de productos
        busqueda = ui.input("Buscar producto", on_change=lambda: cargar_productos(busqueda.value))
        tabla = ui.table(
            columns=[
                {"name": "codigo", "label": "Código", "field": "codigo"},
                {"name": "descripcion", "label": "Descripción", "field": "descripcion"},
                {"name": "precio_venta", "label": "Precio", "field": "precio_venta", "align": "right"},
                {"name": "accion", "label": "Agregar", "field": "accion"},
            ],
            rows=[],
            row_key="id",
        )
        cantidad_input = ui.number("Cantidad", value=1, min=0.01)
        
        def cargar_productos(texto):
            if texto:
                prods = ejecutar_consulta(
                    "SELECT id, codigo, descripcion, precio_venta FROM productos WHERE descripcion LIKE ? AND activo=1 LIMIT 50",
                    (f"%{texto}%",)
                )
            else:
                prods = ejecutar_consulta("SELECT id, codigo, descripcion, precio_venta FROM productos WHERE activo=1 LIMIT 50")
            for p in prods:
                p["accion"] = f'<button onclick="agregarProducto({p["id"]}, {cantidad_input.value})">+</button>'
            tabla.rows = prods
        
        def agregar_al_carrito_desde_popup(producto_id, cantidad):
            producto = ejecutar_consulta("SELECT id, precio_venta FROM productos WHERE id = ?", (producto_id,))[0]
            agregar_al_carrito(usuario["id"], cliente_id, producto_id, cantidad, producto["precio_venta"])
            ui.notify(f"Agregado {cantidad} unidades", type="positive")
        
        # Necesitamos inyectar JavaScript para manejar el botón, pero por simplicidad usamos un botón por fila con evento
        # Mejor usar ui.button en cada fila, pero es más complejo. Usaremos un enfoque con `ui.column` y botones por cada producto.
        # Dado que es un ejemplo, cambio a una lista simple con botones.
        # Reescribo la función cargar_productos usando un `ui.column` dinámico.
        # Por simplicidad final, muestro solo un grid de productos con botón "Agregar".
        dialog.clear()
        with dialog, ui.card():
            ui.label(f"Catálogo para {cliente['razon_social']}").classes("text-h6")
            busqueda = ui.input("Buscar producto")
            productos_container = ui.column()
            def mostrar_productos():
                productos_container.clear()
                texto = busqueda.value
                if texto:
                    prods = ejecutar_consulta("SELECT id, codigo, descripcion, precio_venta FROM productos WHERE descripcion LIKE ? AND activo=1 LIMIT 30", (f"%{texto}%",))
                else:
                    prods = ejecutar_consulta("SELECT id, codigo, descripcion, precio_venta FROM productos WHERE activo=1 LIMIT 30")
                for p in prods:
                    with productos_container:
                        with ui.row().classes("items-center"):
                            ui.label(f"{p['codigo']} - {p['descripcion']} - ${p['precio_venta']:.2f}")
                            cantidad = ui.number(value=1, min=0.01, step=0.5).classes("w-20")
                            ui.button("Agregar", on_click=lambda pid=p['id'], cant=cantidad: agregar_al_carrito_desde_popup(pid, cant.value))
            busqueda.on_change(mostrar_productos)
            mostrar_productos()
            ui.separator()
            with ui.row():
                ui.button("Finalizar pedido", on_click=lambda: finalizar_pedido(dialog, cliente_id), color="primary")
                ui.button("Cancelar", on_click=dialog.close)
    dialog.open()

def finalizar_pedido(dialog, cliente_id):
    from pedidos import crear_nota_venta
    from auth import obtener_usuario_actual, obtener_preventista_id
    usuario = obtener_usuario_actual()
    preventista_id = obtener_preventista_id()
    if not preventista_id:
        ui.notify("No se pudo determinar el preventista", type="error")
        return
    nota_id = crear_nota_venta(usuario["id"], preventista_id, cliente_id)
    if nota_id:
        ui.notify(f"Nota de venta {nota_id} creada exitosamente", type="positive")
        dialog.close()
    else:
        ui.notify("No hay productos en el carrito", type="warning")