"""
Código Crítico - Tercer Semestre - Año 2026
Ventana de catálogo - Diseño minimalista sin degradados
Colores sólidos y bordes definidos
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QWidget,
                             QGridLayout, QSpinBox, QMessageBox, QFrame,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor
from database import ejecutar_consulta
from pedidos import agregar_al_carrito, obtener_carrito, vaciar_carrito
from auth import obtener_usuario_actual
from ventana_resumen_compra import ResumenCompraDialog


# ============================================================
# Función para mostrar mensajes con estilo visible
# ============================================================
def mostrar_mensaje(titulo, mensaje, icono=QMessageBox.Icon.Information, botones=QMessageBox.StandardButton.Ok):
    """Muestra un QMessageBox con estilo visible y botones personalizables"""
    msg = QMessageBox()
    msg.setWindowTitle(titulo)
    msg.setText(mensaje)
    msg.setIcon(icono)
    msg.setStandardButtons(botones)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #f0f2f5;
        }
        QMessageBox QLabel {
            color: #1a2634;
            font-size: 13px;
        }
        QMessageBox QPushButton {
            background-color: #4a90d9;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
            font-weight: 600;
            font-size: 13px;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #3a7bc8;
        }
        QMessageBox QPushButton:pressed {
            background-color: #2a6ab5;
        }
    """)
    return msg.exec()


# ============================================================
# Tarjeta de producto - Diseño sólido
# ============================================================
class TarjetaProducto(QWidget):
    def __init__(self, producto, cliente_id, parent=None):
        super().__init__(parent)
        self.producto = producto
        self.cliente_id = cliente_id
        self.dialog_parent = parent
        
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #d0d5dd;
            }
            QWidget:hover {
                border: 2px solid #4a90d9;
                background-color: #f7f9fc;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(14, 14, 14, 14)
        
        # Imagen
        self.label_imagen = QLabel()
        self.label_imagen.setFixedSize(130, 130)
        self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagen.setStyleSheet("""
            border: 1px solid #e0e4ea;
            border-radius: 6px;
            background-color: #f5f6f8;
        """)
        self.label_imagen.setScaledContents(True)
        layout.addWidget(self.label_imagen, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.mostrar_imagen()
        
        # Código
        lbl_codigo = QLabel(f"<b>{producto['codigo']}</b>")
        lbl_codigo.setStyleSheet("color: #1a2634; font-size: 13px;")
        layout.addWidget(lbl_codigo)
        
        # Descripción
        lbl_desc = QLabel(producto['descripcion'])
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #3d4a5c; font-size: 13px;")
        layout.addWidget(lbl_desc)
        
        # Detalle (opcional)
        if producto.get('detalle'):
            detalle_text = producto['detalle'][:60] + "..." if len(producto['detalle']) > 60 else producto['detalle']
            lbl_detalle = QLabel(detalle_text)
            lbl_detalle.setWordWrap(True)
            lbl_detalle.setStyleSheet("color: #6b7a8a; font-size: 11px; font-style: italic;")
            layout.addWidget(lbl_detalle)
        
        # Precio
        lbl_precio = QLabel(f"<b>${producto['precio_venta']:.2f}</b>")
        lbl_precio.setStyleSheet("color: #d4761a; font-size: 19px;")
        layout.addWidget(lbl_precio)
        
        # Cantidad y botón
        cantidad_layout = QHBoxLayout()
        cantidad_layout.setSpacing(8)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(9999)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setFixedWidth(55)
        self.spin_cantidad.setStyleSheet("""
            QSpinBox {
                border: 1px solid #c5cdd8;
                border-radius: 4px;
                padding: 3px;
                font-size: 13px;
                background-color: #ffffff;
                color: #1a2634;
            }
            QSpinBox:focus {
                border-color: #4a90d9;
            }
        """)
        
        btn_agregar = QPushButton("Agregar")
        btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2a6ab5;
            }
        """)
        btn_agregar.clicked.connect(self.agregar)
        
        cantidad_layout.addWidget(self.spin_cantidad)
        cantidad_layout.addWidget(btn_agregar)
        layout.addLayout(cantidad_layout)
        
        self.setLayout(layout)
        self.setFixedWidth(210)
    
    def mostrar_imagen(self):
        codigo = self.producto.get('codigo')
        if not codigo:
            self._mostrar_placeholder()
            return
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        carpeta_fotos = os.path.join(base_dir, "imagenes_productos")
        
        extensiones = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        ruta_imagen = None
        
        for ext in extensiones:
            ruta = os.path.join(carpeta_fotos, f"{codigo}{ext}")
            if os.path.exists(ruta):
                ruta_imagen = ruta
                break
        
        if ruta_imagen:
            pixmap = QPixmap(ruta_imagen)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                self.label_imagen.setPixmap(pixmap)
                return
        
        self._mostrar_placeholder()
    
    def _mostrar_placeholder(self):
        pixmap = QPixmap(130, 130)
        pixmap.fill(QColor(240, 242, 245))
        self.label_imagen.setPixmap(pixmap)
    
    def agregar(self):
        usuario = obtener_usuario_actual()
        if not usuario:
            mostrar_mensaje("Error", "No hay usuario autenticado.", QMessageBox.Icon.Critical)
            return
        cantidad = self.spin_cantidad.value()
        # ✅ CORREGIDO: Usar 'codigo' en lugar de 'id'
        agregar_al_carrito(usuario['id'], self.cliente_id, 
                          self.producto['codigo'], cantidad, self.producto['precio_venta'])
        if self.dialog_parent and hasattr(self.dialog_parent, 'actualizar_carrito'):
            self.dialog_parent.actualizar_carrito()


# ============================================================
# Ventana principal del catálogo - Sin degradados
# ============================================================
class CatalogoDialog(QDialog):
    def __init__(self, cliente_id, cliente_nombre, parent=None):
        super().__init__(parent)
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre
        self.setWindowTitle(f"Catálogo - {cliente_nombre}")
        self.setFixedSize(1350, 850)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Fondo sólido gris claro
        self.setStyleSheet("""
            QDialog {
                background-color: #eef0f2;
                border: 2px solid #c8cdd4;
                border-radius: 12px;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ============================================================
        # COLUMNA IZQUIERDA: Productos
        # ============================================================
        col_productos = QVBoxLayout()
        col_productos.setSpacing(12)
        
        # Encabezado
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #d0d5dd;
                padding: 4px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)
        
        lbl_titulo = QLabel("📦 Catálogo de Productos")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: 700; color: #1a2634;")
        header_layout.addWidget(lbl_titulo)
        
        lbl_cliente = QLabel(f"Cliente: {cliente_nombre}")
        lbl_cliente.setStyleSheet("""
            font-size: 13px;
            color: #3d4a5c;
            background-color: #eef0f2;
            padding: 4px 14px;
            border-radius: 4px;
            border: 1px solid #d0d5dd;
        """)
        header_layout.addWidget(lbl_cliente)
        
        col_productos.addWidget(header_frame)
        
        # Barra de búsqueda
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 6px;
                border: 1px solid #d0d5dd;
            }
            QFrame:focus-within {
                border-color: #4a90d9;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 2, 6, 2)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; padding: 0 4px;")
        search_layout.addWidget(search_icon)
        
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Buscar por código o descripción...")
        self.busqueda_input.setMinimumHeight(36)
        self.busqueda_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 4px;
                font-size: 14px;
                background-color: transparent;
                color: #1a2634;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.busqueda_input.textChanged.connect(self.cargar_productos)
        search_layout.addWidget(self.busqueda_input)
        
        btn_limpiar = QPushButton("✕")
        btn_limpiar.setFixedSize(26, 26)
        btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpiar.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 13px;
                background-color: #e8eaed;
                color: #6b7a8a;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #d5d8dd;
            }
        """)
        btn_limpiar.clicked.connect(lambda: self.busqueda_input.clear())
        search_layout.addWidget(btn_limpiar)
        
        col_productos.addWidget(search_frame)
        
        # Contador
        self.lbl_resultados = QLabel("Mostrando todos los productos")
        self.lbl_resultados.setStyleSheet("color: #6b7a8a; font-size: 12px; padding: 0 4px;")
        col_productos.addWidget(self.lbl_resultados)
        
        # ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #e8eaed;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c5cdd8;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8b2c0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.contenedor = QWidget()
        self.contenedor.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.contenedor)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.contenedor)
        col_productos.addWidget(self.scroll_area)
        
        # ============================================================
        # COLUMNA DERECHA: Carrito
        # ============================================================
        col_carrito = QVBoxLayout()
        col_carrito.setSpacing(0)
        col_carrito.setContentsMargins(0, 0, 0, 0)
        
        frame_carrito = QFrame()
        frame_carrito.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #d0d5dd;
            }
        """)
        frame_carrito.setFixedWidth(300)
        frame_carrito.setMinimumHeight(500)
        
        carrito_layout = QVBoxLayout(frame_carrito)
        carrito_layout.setSpacing(10)
        carrito_layout.setContentsMargins(16, 16, 16, 16)
        
        # Encabezado carrito
        carrito_header = QHBoxLayout()
        
        lbl_carrito = QLabel("🛒 Carrito")
        lbl_carrito.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #1a2634;
        """)
        carrito_header.addWidget(lbl_carrito)
        
        self.lbl_items = QLabel("0 items")
        self.lbl_items.setStyleSheet("""
            background-color: #4a90d9;
            color: #ffffff;
            border-radius: 10px;
            padding: 1px 12px;
            font-size: 12px;
            font-weight: 600;
        """)
        carrito_header.addWidget(self.lbl_items)
        carrito_header.addStretch()
        
        carrito_layout.addLayout(carrito_header)
        
        # Línea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #e0e4ea; max-height: 1px;")
        carrito_layout.addWidget(linea)
        
        # Lista del carrito
        self.lista_carrito = QListWidget()
        self.lista_carrito.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 13px;
                color: #1a2634;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 6px;
                border-bottom: 1px solid #f0f2f4;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e8edf5;
                color: #1a2634;
            }
            QListWidget::item:hover {
                background-color: #f5f6f8;
            }
        """)
        self.lista_carrito.setMinimumHeight(200)
        carrito_layout.addWidget(self.lista_carrito)
        
        # Resumen total
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #f7f8fa;
                border-radius: 6px;
                border: 1px solid #e8eaed;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(12, 10, 12, 10)
        
        lbl_total_text = QLabel("TOTAL")
        lbl_total_text.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a2634;")
        total_layout.addWidget(lbl_total_text)
        total_layout.addStretch()
        
        self.lbl_total = QLabel("$0.00")
        self.lbl_total.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #d4761a;
        """)
        total_layout.addWidget(self.lbl_total)
        
        carrito_layout.addWidget(total_frame)
        
        # Botones
        btn_vaciar = QPushButton("Vaciar carrito")
        btn_vaciar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_vaciar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 9px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d44235;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        btn_vaciar.clicked.connect(self.vaciar_carrito)
        carrito_layout.addWidget(btn_vaciar)
        
        btn_finalizar = QPushButton("Finalizar Compra")
        btn_finalizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 11px;
                font-weight: 700;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        btn_finalizar.clicked.connect(self.finalizar_compra)
        carrito_layout.addWidget(btn_finalizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 9px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6b7a7a;
            }
            QPushButton:pressed {
                background-color: #5a6a6a;
            }
        """)
        btn_cerrar.clicked.connect(self.reject)
        carrito_layout.addWidget(btn_cerrar)
        
        col_carrito.addWidget(frame_carrito)
        
        main_layout.addLayout(col_productos, 4)
        main_layout.addLayout(col_carrito, 1)
        
        self.setLayout(main_layout)
        
        self.cargar_productos()
        self.actualizar_carrito()
        
        # Variables para arrastrar la ventana
        self.drag_pos = None
        self.drag_start = None
    
    def cargar_productos(self):
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        texto = self.busqueda_input.text().strip()
        if texto:
            productos = ejecutar_consulta(
                "SELECT id, codigo, descripcion, precio_venta, detalle FROM productos WHERE (codigo LIKE ? OR descripcion LIKE ?) AND activo=1 ORDER BY descripcion LIMIT 200",
                (f'%{texto}%', f'%{texto}%')
            )
        else:
            productos = ejecutar_consulta(
                "SELECT id, codigo, descripcion, precio_venta, detalle FROM productos WHERE activo=1 ORDER BY descripcion LIMIT 200"
            )
        
        if productos:
            self.lbl_resultados.setText(f"Mostrando {len(productos)} productos")
        else:
            self.lbl_resultados.setText("No se encontraron productos")
        
        if not productos:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_icon = QLabel("🔍")
            empty_icon.setStyleSheet("font-size: 48px;")
            empty_layout.addWidget(empty_icon, alignment=Qt.AlignmentFlag.AlignCenter)
            
            empty_msg = QLabel("No se encontraron productos")
            empty_msg.setStyleSheet("color: #8a9aa8; font-size: 18px; font-weight: 500;")
            empty_layout.addWidget(empty_msg, alignment=Qt.AlignmentFlag.AlignCenter)
            
            self.grid_layout.addWidget(empty_widget, 0, 0, 1, 1)
            return
        
        cols = 4
        for idx, prod in enumerate(productos):
            tarjeta = TarjetaProducto(prod, self.cliente_id, self)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(tarjeta, row, col)
    
    def actualizar_carrito(self):
        usuario = obtener_usuario_actual()
        if not usuario:
            return
        
        items = obtener_carrito(usuario['id'], self.cliente_id)
        self.lista_carrito.clear()
        
        total = 0
        total_items = 0
        for item in items:
            # ✅ CORREGIDO: Buscar por codigo en lugar de id
            prod = ejecutar_consulta("SELECT descripcion FROM productos WHERE codigo = ?", (item['codigo_producto'],))
            desc = prod[0]['descripcion'] if prod else f"Producto {item['codigo_producto']}"
            subtotal = item['cantidad'] * item['precio_unitario']
            total += subtotal
            total_items += item['cantidad']
            
            item_text = f"{desc[:30]}{'...' if len(desc) > 30 else ''}  ×{item['cantidad']}"
            self.lista_carrito.addItem(item_text)
        
        self.lbl_total.setText(f"${total:.2f}")
        self.lbl_items.setText(f"{total_items} items")
    
    def vaciar_carrito(self):
        """Vacía el carrito de compras con confirmación"""
        usuario = obtener_usuario_actual()
        if not usuario:
            mostrar_mensaje("Error", "No hay usuario autenticado.", QMessageBox.Icon.Critical)
            return
        
        # Verificar si el carrito está vacío
        if self.lista_carrito.count() == 0:
            mostrar_mensaje("Carrito vacío", "El carrito ya está vacío.", QMessageBox.Icon.Information)
            return
        
        # Confirmar antes de vaciar
        msg = QMessageBox()
        msg.setWindowTitle("Confirmar")
        msg.setText("¿Estás seguro de que deseas vaciar el carrito?\n\nEsta acción no se puede deshacer.")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f2f5;
            }
            QMessageBox QLabel {
                color: #1a2634;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QMessageBox QPushButton[text="&Yes"] {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QMessageBox QPushButton[text="&Yes"]:hover {
                background-color: #d44235;
            }
            QMessageBox QPushButton[text="&No"] {
                background-color: #7f8c8d;
                color: #ffffff;
            }
            QMessageBox QPushButton[text="&No"]:hover {
                background-color: #6b7a7a;
            }
        """)
        
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            vaciar_carrito(usuario['id'], self.cliente_id)
            self.actualizar_carrito()
            mostrar_mensaje("🛒 Carrito vacío", "Se han eliminado todos los productos del carrito.", QMessageBox.Icon.Information)
    
    def finalizar_compra(self):
        usuario = obtener_usuario_actual()
        if not usuario:
            mostrar_mensaje("Error", "No hay usuario autenticado.", QMessageBox.Icon.Critical)
            return
        
        items = obtener_carrito(usuario['id'], self.cliente_id)
        if not items:
            mostrar_mensaje("Carrito vacío", "No hay productos agregados al carrito.", QMessageBox.Icon.Warning)
            return
        
        items_con_detalle = []
        total = 0
        for item in items:
            # ✅ CORREGIDO: Buscar por codigo en lugar de id
            producto = ejecutar_consulta("SELECT descripcion FROM productos WHERE codigo = ?", (item['codigo_producto'],))
            if producto:
                descripcion = producto[0]['descripcion']
                items_con_detalle.append({
                    'descripcion': descripcion,
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario']
                })
                total += item['cantidad'] * item['precio_unitario']
        
        cliente = ejecutar_consulta("SELECT id, razon_social, cuit, telefono, email FROM clientes WHERE id = ?", (self.cliente_id,))
        if not cliente:
            mostrar_mensaje("Error", "Cliente no encontrado.", QMessageBox.Icon.Critical)
            return
        
        resumen = ResumenCompraDialog(usuario, cliente[0], items_con_detalle, total, self)
        if resumen.exec():
            vaciar_carrito(usuario['id'], self.cliente_id)
            self.accept()
    
    # Métodos para arrastrar la ventana
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            self.drag_start = self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.drag_start + delta)