"""
Código Crítico - Tercer Semestre - Año 2026
Pantalla de bienvenida (Splash Screen) con diseño moderno y colores oscuros.
Ventana redonda, letras blancas grandes debajo de la barra de progreso.
"""

import os
import time
from PyQt6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QRect
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QConicalGradient, QBrush, 
    QPainterPath, QLinearGradient  # <--- AGREGADO
)

class SpinnerWidget(QWidget):
    def __init__(self, parent=None, size=70):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotar)
        self.timer.start(30)
        self.setStyleSheet("background: transparent;")
    
    def rotar(self):
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        centro = self.width() // 2
        radio = self.width() // 2 - 5
        
        gradient = QConicalGradient(centro, centro, self.angle)
        gradient.setColorAt(0.0, QColor(0, 210, 255))
        gradient.setColorAt(0.3, QColor(0, 150, 255))
        gradient.setColorAt(0.6, QColor(100, 100, 255))
        gradient.setColorAt(1.0, QColor(30, 30, 60))
        
        pen = QPen(QBrush(gradient), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(centro - radio, centro - radio, radio * 2, radio * 2, 0, 360 * 16)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(26, 26, 46))
        painter.drawEllipse(centro - radio + 8, centro - radio + 8, (radio - 8) * 2, (radio - 8) * 2)


class SplashBienvenida(QSplashScreen):
    terminado = pyqtSignal()
    
    def __init__(self):
        # Crear pixmap redondo primero
        size = 500
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Dibujar fondo redondo
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Usar QLinearGradient correctamente
        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0.0, QColor(26, 26, 46))
        gradient.setColorAt(1.0, QColor(22, 33, 62))
        painter.fillRect(0, 0, size, size, gradient)
        painter.end()
        
        # Llamar al constructor de QSplashScreen con el pixmap
        super().__init__(pixmap)
        
        # Ahora configurar los flags de ventana
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(size, size)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        titulo = QLabel("Catálogo Virtual")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 1px;
        """)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Sistema de Gestión de Pedidos")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("""
            font-size: 14px;
            color: #8a8aaa;
            margin-bottom: 10px;
        """)
        layout.addWidget(subtitulo)
        
        # Spinner
        self.spinner = SpinnerWidget(self, 60)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(280)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 2px;
                background-color: #2a2a4a;
            }
            QProgressBar::chunk {
                background-color: #00d2ff;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Texto de carga (abajo de la barra, más grande y blanco)
        self.label_carga = QLabel("Iniciando sistema...")
        self.label_carga.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_carga.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 12px;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.label_carga)
        
        # Widget central para aplicar el layout
        central = QWidget(self)
        central.setGeometry(0, 0, size, size)
        central.setLayout(layout)
        
        self.center()
        
        self.progreso = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_progreso)
        self.timer.start(50)
        
        self._sincronizacion_iniciada = False
        self.show()
    
    def center(self):
        pantalla = self.screen().availableGeometry()
        x = (pantalla.width() - self.width()) // 2
        y = (pantalla.height() - self.height()) // 2
        self.move(x, y)
    
    def sincronizar_todo(self):
        if self._sincronizacion_iniciada:
            return
        self._sincronizacion_iniciada = True
        
        from sync import bajar_tabla
        
        tablas = [
            ('usuarios', '👤 Usuarios y contraseñas'),
            ('preventistas', '👨‍💼 Preventistas'),
            ('clientes', '🏢 Clientes'),
            ('productos', '📦 Productos (stock y precios)'),
            ('categorias', '📂 Categorías'),
            ('lotes', '🔢 Números de lote')
        ]
        
        total = len(tablas)
        for i, (tabla, descripcion) in enumerate(tablas):
            porcentaje = int((i + 1) / total * 80) + 10
            self.label_carga.setText(f"🔄 {descripcion}...")
            self.progress_bar.setValue(porcentaje)
            try:
                bajar_tabla(tabla)
                print(f"✅ {tabla} sincronizado correctamente")
            except Exception as e:
                print(f"⚠️ Error sincronizando {tabla}: {e}")
            time.sleep(0.2)
        
        self.label_carga.setText("✅ Sistema listo!")
        self.progress_bar.setValue(100)
        time.sleep(0.5)
        self.close()
        self.terminado.emit()
    
    def actualizar_progreso(self):
        self.progreso += 1
        self.progress_bar.setValue(self.progreso)
        
        if self.progreso < 5:
            self.label_carga.setText("🚀 Iniciando sistema...")
        elif self.progreso < 10:
            self.label_carga.setText("📡 Conectando con Turso...")
        elif self.progreso < 20:
            self.label_carga.setText("👤 Actualizando usuarios...")
        elif self.progreso < 30:
            self.label_carga.setText("👨‍💼 Actualizando preventistas...")
        elif self.progreso < 45:
            self.label_carga.setText("🏢 Actualizando clientes...")
        elif self.progreso < 60:
            self.label_carga.setText("📦 Actualizando stock y precios...")
        elif self.progreso < 75:
            self.label_carga.setText("📂 Actualizando categorías...")
        elif self.progreso < 90:
            self.label_carga.setText("🔢 Actualizando lotes...")
        else:
            self.label_carga.setText("✅ ¡Listo!")
        
        if self.progreso >= 100:
            self.timer.stop()
            self.spinner.timer.stop()
            if not self._sincronizacion_iniciada:
                self.sincronizar_todo()