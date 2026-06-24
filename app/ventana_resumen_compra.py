"""
Código Crítico - Tercer Semestre - Año 2026
Ventana de resumen de compra - Diseño limpio y legible
Tamaño: 1000x800
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFrame, QWidget,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from pedidos import crear_nota_venta


# ============================================================
# Función para mostrar mensajes con estilo visible
# ============================================================
def mostrar_mensaje(titulo, mensaje, icono=QMessageBox.Icon.Information):
    """Muestra un QMessageBox con estilo visible"""
    msg = QMessageBox()
    msg.setWindowTitle(titulo)
    msg.setText(mensaje)
    msg.setIcon(icono)
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


class ResumenCompraDialog(QDialog):
    def __init__(self, usuario, cliente, items, total, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.cliente = cliente
        self.items = items
        self.total = total
        self.setWindowTitle("Confirmar Compra")
        self.setFixedSize(1000, 800)  # Tamaño corregido
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        
        # Fondo sólido
        self.setStyleSheet("""
            QDialog {
                background-color: #eef0f2;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # ===== TÍTULO =====
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #1a2634;
                border-radius: 12px;
            }
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(20, 12, 20, 12)
        
        title_icon = QLabel("📋")
        title_icon.setStyleSheet("font-size: 26px;")
        title_layout.addWidget(title_icon)
        
        title = QLabel("Resumen de la Compra")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        nota_label = QLabel("Nueva Nota de Venta")
        nota_label.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            font-size: 13px;
            font-weight: 400;
            background-color: rgba(255,255,255,0.12);
            border-radius: 16px;
            padding: 4px 14px;
        """)
        title_layout.addWidget(nota_label)
        
        layout.addWidget(title_container)
        
        # ===== INFO CLIENTE Y PREVENTISTA =====
        info_container = QHBoxLayout()
        info_container.setSpacing(15)
        
        # Cliente
        cliente_card = QFrame()
        cliente_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #d0d5dd;
            }
        """)
        cliente_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        cliente_layout = QVBoxLayout(cliente_card)
        cliente_layout.setContentsMargins(16, 12, 16, 12)
        cliente_layout.setSpacing(5)
        
        cliente_header = QHBoxLayout()
        cliente_icon = QLabel("👤")
        cliente_icon.setStyleSheet("font-size: 16px;")
        cliente_header.addWidget(cliente_icon)
        
        cliente_title = QLabel("CLIENTE")
        cliente_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #4a90d9;
            letter-spacing: 0.5px;
        """)
        cliente_header.addWidget(cliente_title)
        cliente_header.addStretch()
        cliente_layout.addLayout(cliente_header)
        
        linea_cliente = QFrame()
        linea_cliente.setFrameShape(QFrame.Shape.HLine)
        linea_cliente.setStyleSheet("background-color: #e8eaed; max-height: 1px; margin: 2px 0;")
        cliente_layout.addWidget(linea_cliente)
        
        cliente_data = QVBoxLayout()
        cliente_data.setSpacing(3)
        
        lbl_razon = QLabel(f"<b style='color:#1a2634;'>Razón Social:</b> <span style='color:#3d4a5c;'>{cliente['razon_social']}</span>")
        lbl_razon.setStyleSheet("font-size: 13px;")
        cliente_data.addWidget(lbl_razon)
        
        cuit_text = cliente.get('cuit', 'N/A')
        lbl_cuit = QLabel(f"<b style='color:#1a2634;'>CUIT:</b> <span style='color:#3d4a5c;'>{cuit_text}</span>")
        lbl_cuit.setStyleSheet("font-size: 13px;")
        cliente_data.addWidget(lbl_cuit)
        
        telefono_text = cliente.get('telefono', 'N/A')
        lbl_telefono = QLabel(f"<b style='color:#1a2634;'>Teléfono:</b> <span style='color:#3d4a5c;'>{telefono_text}</span>")
        lbl_telefono.setStyleSheet("font-size: 13px;")
        cliente_data.addWidget(lbl_telefono)
        
        email_text = cliente.get('email', 'N/A')
        lbl_email = QLabel(f"<b style='color:#1a2634;'>Email:</b> <span style='color:#3d4a5c;'>{email_text}</span>")
        lbl_email.setStyleSheet("font-size: 13px;")
        cliente_data.addWidget(lbl_email)
        
        cliente_layout.addLayout(cliente_data)
        
        # Preventista
        preventista_card = QFrame()
        preventista_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #d0d5dd;
            }
        """)
        preventista_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        preventista_layout = QVBoxLayout(preventista_card)
        preventista_layout.setContentsMargins(16, 12, 16, 12)
        preventista_layout.setSpacing(5)
        
        prev_header = QHBoxLayout()
        prev_icon = QLabel("👨‍💼")
        prev_icon.setStyleSheet("font-size: 16px;")
        prev_header.addWidget(prev_icon)
        
        prev_title = QLabel("PREVENTISTA")
        prev_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 700;
            color: #27ae60;
            letter-spacing: 0.5px;
        """)
        prev_header.addWidget(prev_title)
        prev_header.addStretch()
        preventista_layout.addLayout(prev_header)
        
        linea_prev = QFrame()
        linea_prev.setFrameShape(QFrame.Shape.HLine)
        linea_prev.setStyleSheet("background-color: #e8eaed; max-height: 1px; margin: 2px 0;")
        preventista_layout.addWidget(linea_prev)
        
        prev_data = QVBoxLayout()
        prev_data.setSpacing(3)
        
        lbl_usuario = QLabel(f"<b style='color:#1a2634;'>Usuario:</b> <span style='color:#3d4a5c;'>{usuario['username']}</span>")
        lbl_usuario.setStyleSheet("font-size: 13px;")
        prev_data.addWidget(lbl_usuario)
        
        prev_id_text = usuario.get('preventista_id', 'N/A')
        lbl_prev_id = QLabel(f"<b style='color:#1a2634;'>ID Preventista:</b> <span style='color:#3d4a5c;'>{prev_id_text}</span>")
        lbl_prev_id.setStyleSheet("font-size: 13px;")
        prev_data.addWidget(lbl_prev_id)
        
        preventista_layout.addLayout(prev_data)
        
        info_container.addWidget(cliente_card, 1)
        info_container.addWidget(preventista_card, 1)
        layout.addLayout(info_container)
        
        # ===== TABLA DE PRODUCTOS =====
        table_header = QHBoxLayout()
        table_title = QLabel("📦 Productos")
        table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1a2634;
        """)
        table_header.addWidget(table_title)
        
        items_count = QLabel(f"{len(self.items)} items")
        items_count.setStyleSheet("""
            background-color: #e8eaed;
            color: #3d4a5c;
            border-radius: 10px;
            padding: 2px 12px;
            font-size: 12px;
            font-weight: 500;
        """)
        table_header.addWidget(items_count)
        table_header.addStretch()
        layout.addLayout(table_header)
        
        # Tabla CORREGIDA - sin fondo negro en los items
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #d0d5dd;
                gridline-color: #e8eaed;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px 10px;
                color: #1a2634;
                background-color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #e8edf5;
                color: #1a2634;
            }
            QTableWidget::item:alternate {
                background-color: #f7f8fa;
            }
            QHeaderView::section {
                background-color: #1a2634;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                padding: 10px 8px;
                border: none;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
        """)
        layout.addWidget(self.tabla)
        
        # Cargar productos
        self.tabla.setRowCount(len(self.items))
        for i, item in enumerate(self.items):
            # Producto
            item_prod = QTableWidgetItem(item['descripcion'])
            item_prod.setForeground(QColor(26, 38, 52))
            item_prod.setBackground(QColor(255, 255, 255))  # Fondo blanco explícito
            font = item_prod.font()
            font.setWeight(500)
            item_prod.setFont(font)
            self.tabla.setItem(i, 0, item_prod)
            
            # Cantidad
            item_cant = QTableWidgetItem(str(item['cantidad']))
            item_cant.setForeground(QColor(26, 38, 52))
            item_cant.setBackground(QColor(255, 255, 255))  # Fondo blanco explícito
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(i, 1, item_cant)
            
            # Precio
            item_precio = QTableWidgetItem(f"${item['precio_unitario']:.2f}")
            item_precio.setForeground(QColor(26, 38, 52))
            item_precio.setBackground(QColor(255, 255, 255))  # Fondo blanco explícito
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(i, 2, item_precio)
            
            # Subtotal
            subtotal = item['cantidad'] * item['precio_unitario']
            item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
            item_subtotal.setForeground(QColor(26, 38, 52))
            item_subtotal.setBackground(QColor(255, 255, 255))  # Fondo blanco explícito
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font_sub = item_subtotal.font()
            font_sub.setWeight(600)
            item_subtotal.setFont(font_sub)
            self.tabla.setItem(i, 3, item_subtotal)
        
        # Ajustar altura de filas
        for i in range(self.tabla.rowCount()):
            self.tabla.setRowHeight(i, 44)
        
        # ===== TOTAL =====
        total_container = QFrame()
        total_container.setStyleSheet("""
            QFrame {
                background-color: #f7f8fa;
                border-radius: 10px;
                border: 2px solid #d0d5dd;
            }
        """)
        total_layout = QHBoxLayout(total_container)
        total_layout.setContentsMargins(24, 14, 24, 14)
        
        total_label_left = QLabel("💰 TOTAL")
        total_label_left.setStyleSheet("""
            font-size: 17px;
            font-weight: 700;
            color: #1a2634;
            letter-spacing: 0.5px;
        """)
        total_layout.addWidget(total_label_left)
        
        total_layout.addStretch()
        
        self.total_label = QLabel(f"${self.total:.2f}")
        self.total_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 800;
            color: #d4761a;
            background-color: rgba(212, 118, 26, 0.08);
            padding: 2px 18px;
            border-radius: 8px;
        """)
        total_layout.addWidget(self.total_label)
        
        layout.addWidget(total_container)
        
        # ===== BOTONES =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_confirmar = QPushButton("✅ Confirmar Compra")
        btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirmar.setMinimumHeight(52)
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        btn_confirmar.clicked.connect(self.confirmar)
        
        btn_cancelar = QPushButton("✕ Cancelar")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setMinimumHeight(52)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #d44235;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_confirmar)
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def confirmar(self):
        nota_id = crear_nota_venta(self.usuario['id'], self.usuario['preventista_id'], self.cliente['id'])
        if nota_id:
            mostrar_mensaje(
                "✅ Compra Confirmada", 
                f"¡Compra realizada con éxito!\n\nNota de venta #{nota_id} creada correctamente.\nSe sincronizará automáticamente con el sistema central.",
                QMessageBox.Icon.Information
            )
            self.accept()
        else:
            mostrar_mensaje(
                "❌ Error", 
                "No se pudo crear la nota de venta.\nEl carrito puede estar vacío o ha ocurrido un error inesperado.",
                QMessageBox.Icon.Critical
            )