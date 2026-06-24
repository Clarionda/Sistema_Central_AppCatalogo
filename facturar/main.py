"""
Código Crítico - Tercer Semestre Año 2026
Punto de entrada principal - Splash redondo y login redondeado
CON ESCALADO GLOBAL NATIVO (QT_SCALE_FACTOR)
CON SELECTOR CIRCULAR DE RESOLUCIÓN
"""

import sys
import os
import math

# Forzar X11 (Wayland no escala bien)
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Forzar escala antes de importar PyQt6
os.environ["QT_SCALE_FACTOR"] = "1.0"

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen, QRegion, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QDialog

# Asegurar el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_manager import inicializar_bd, obtener_conexion
from modelos.usuario import crear_usuario_admin


# ============================================================
# SELECTOR CIRCULAR CON PROGRESO
# ============================================================

class SelectorCircularEscala(QSplashScreen):
    def __init__(self):
        self.radius = 220
        pixmap = QPixmap(480, 480)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setMask(QRegion(0, 0, 480, 480, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)

        self.angulo = 0
        self.progreso = 0
        self.escala_seleccionada = 1.0
        self.seleccionado = False
        self.texto = "🖥️ SELECCIONE RESOLUCIÓN"
        self.opciones = [
            {"texto": "MEDIANO\n100%", "escala": 1.0, "color": "#2196F3"},
            {"texto": "GRANDE\n130%", "escala": 1.3, "color": "#4CAF50"},
            {"texto": "MUY GRANDE\n160%", "escala": 1.6, "color": "#FF9800"}
        ]
        self.opcion_seleccionada = None

        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulo)
        self.timer_animacion.start(50)

        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso)

        self.show()
        QApplication.processEvents()

    def _actualizar_angulo(self):
        self.angulo = (self.angulo + 4) % 360
        self.update()

    def _actualizar_progreso(self):
        if self.progreso < 100:
            self.progreso += 2
            self.update()
        else:
            self.timer_progreso.stop()
            self.timer_animacion.stop()
            QTimer.singleShot(300, self.close)

    def iniciar_progreso(self):
        self.progreso = 0
        self.timer_progreso.start(30)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio_interno = 80
        radio_externo = 180

        dist = ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5
        if radio_interno < dist < radio_externo:
            ang = (math.atan2(y - centro_y, x - centro_x) * 180 / math.pi + 90) % 360
            
            if 0 <= ang < 120:
                idx = 0
            elif 120 <= ang < 240:
                idx = 1
            else:
                idx = 2
            
            self.opcion_seleccionada = idx
            self.escala_seleccionada = self.opciones[idx]["escala"]
            self.seleccionado = True
            self.texto = f"✅ {self.opciones[idx]['texto']}"
            self.iniciar_progreso()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 200

        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(1, QColor(13, 71, 161))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        pen = QPen()
        pen.setWidth(3)

        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 160, centro_y - 160, 320, 320,
                       self.angulo * 16, 100 * 16)

        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 140, centro_y - 140, 280, 280,
                       (360 - self.angulo) * 16, 80 * 16)

        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 120, centro_y - 120, 240, 240,
                       (self.angulo + 180) * 16, 70 * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        op_radio = 130
        for i, op in enumerate(self.opciones):
            angulo = -90 + i * 120
            rad = math.radians(angulo)
            x = centro_x + op_radio * math.cos(rad)
            y = centro_y + op_radio * math.sin(rad)
            
            color = QColor(op["color"])
            
            if self.opcion_seleccionada == i:
                color = QColor(255, 193, 7)
                radio_op = 55
            else:
                radio_op = 50
            
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x - radio_op), int(y - radio_op), int(radio_op * 2), int(radio_op * 2))
            
            painter.setFont(QFont("Segoe UI", 10 if self.opcion_seleccionada != i else 11, 
                                   QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255))
            
            lineas = op["texto"].split("\n")
            for j, linea in enumerate(lineas):
                rect = QRect(int(x - 50), int(y - 20 + j * 20), 100, 25)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, linea)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.drawEllipse(centro_x - 50, centro_y - 50, 100, 100)

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(26, 35, 126))
        
        if self.seleccionado:
            texto_mostrar = self.texto
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        else:
            texto_mostrar = "🖥️\nToca\nuna opción"
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        rect_centro = QRect(centro_x - 45, centro_y - 30, 90, 60)
        painter.drawText(rect_centro, Qt.AlignmentFlag.AlignCenter, texto_mostrar)

        if self.progreso > 0:
            pen.setWidth(8)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso / 100)
            painter.drawArc(centro_x - 90, centro_y - 90, 180, 180,
                          90 * 16, angulo_fin * 16)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 200)))
            painter.drawEllipse(centro_x - 25, centro_y + 50, 50, 30)
            
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255))
            rect_pct = QRect(centro_x - 25, centro_y + 50, 50, 30)
            painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, f"{self.progreso}%")
        
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 150, centro_y + 130, 300, 20),
                        Qt.AlignmentFlag.AlignCenter, "Seleccione una resolución")
        
        if self.seleccionado:
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor(255, 193, 7))
            painter.drawText(QRect(centro_x - 150, centro_y + 150, 300, 20),
                            Qt.AlignmentFlag.AlignCenter, "⏳ Aplicando configuración...")


# ============================================================
# SPLASH DE INICIO
# ============================================================

class SplashScreenConAnimacion(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        self.setMask(QRegion(QRect(0, 0, 400, 400), QRegion.RegionType.Ellipse))
        self.angulo = 0
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.SplashScreen)
        self.setStyleSheet("background: transparent;")
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.actualizar_angulo)
        self.timer_animacion.start(50)

    def actualizar_angulo(self):
        self.angulo = (self.angulo + 6) % 360
        self.update()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 180

        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(1, QColor(13, 71, 161))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 140, centro_y - 140, 280, 280, self.angulo * 16, 120 * 16)

        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 120, centro_y - 120, 240, 240, (360 - self.angulo) * 16, 90 * 16)

        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 100, centro_y - 100, 200, 200, (self.angulo + 180) * 16, 80 * 16)

        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - 35, centro_y - 35, 70, 70)

        painter.setPen(QPen(QColor(26, 35, 126), 3))
        painter.setBrush(QBrush(QColor(255, 193, 7)))
        painter.drawRect(centro_x - 20, centro_y - 25, 35, 18)
        painter.drawRect(centro_x + 3, centro_y - 18, 14, 10)

        painter.setBrush(QBrush(QColor(33, 33, 33)))
        painter.drawEllipse(centro_x - 14, centro_y - 14, 8, 8)
        painter.drawEllipse(centro_x + 8, centro_y - 14, 8, 8)

        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(centro_x - 150, centro_y + 30, 300, 40), Qt.AlignmentFlag.AlignCenter, "Sistema de")

        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(QRect(centro_x - 150, centro_y + 55, 300, 40), Qt.AlignmentFlag.AlignCenter, "Distribución y Logística")

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 150, centro_y + 85, 300, 20), Qt.AlignmentFlag.AlignCenter, "v3.0.0 - Código Crítico")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(255, 193, 7))
        painter.drawText(QRect(centro_x - 150, centro_y + 115, 300, 20), Qt.AlignmentFlag.AlignCenter, "Iniciando sistema...")

    def cerrar(self):
        self.timer_animacion.stop()
        self.hide()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 60)
    print("   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA")
    print("   Código Crítico - Tercer Semestre 2026")
    print("=" * 60)

    # ============================================================
    # 1. INICIALIZAR BASE DE DATOS
    # ============================================================
    print("\n📁 Inicializando base de datos...")
    inicializar_bd()
    print("✅ Base de datos lista.")

    db = obtener_conexion()
    crear_usuario_admin(db)
    db.close()

    # ============================================================
    # 2. MOSTRAR SELECTOR CIRCULAR DE ESCALA
    # ============================================================
    app_temp = QApplication(sys.argv)
    app_temp.setStyle("Fusion")

    selector = SelectorCircularEscala()
    
    while not selector.seleccionado:
        app_temp.processEvents()
        if selector.isHidden():
            break
    
    while selector.progreso < 100 and not selector.isHidden():
        app_temp.processEvents()
    
    factor_escala = selector.escala_seleccionada
    print(f"📐 Factor de escala seleccionado: {factor_escala}")

    selector.close()
    app_temp.quit()
    app_temp = None

    # ============================================================
    # 3. APLICAR ESCALA GLOBAL
    # ============================================================
    os.environ["QT_SCALE_FACTOR"] = str(factor_escala)
    os.environ["QT_FONT_DPI"] = str(int(96 * factor_escala))

    print(f"✅ Escala global aplicada: {factor_escala * 100}%")
    print(f"📐 QT_SCALE_FACTOR = {os.environ.get('QT_SCALE_FACTOR')}")

    # ============================================================
    # 4. IMPORTAR MÓDULOS
    # ============================================================
    from vistas.ventana_principal import VentanaPrincipal, DialogoLogin
    
    # ============================================================
    # 5. INICIAR SINCRONIZACIÓN CON TURSO
    # ============================================================
    try:
        from utilidades.central_sync import iniciar_sincronizacion_auto, sincronizar_desde_central
        
        # Iniciar sincronización automática (cada 3 segundos)
        iniciar_sincronizacion_auto()
        print("✅ Sincronización automática iniciada")
        
        # Sincronizar datos iniciales desde Central a Turso
        print("📤 Sincronizando datos iniciales con Turso...")
        sincronizar_desde_central()
        print("✅ Datos iniciales sincronizados con Turso")
        
    except Exception as e:
        print(f"⚠️ Error al iniciar sincronización: {e}")

    # ============================================================
    # 6. CREAR APP FINAL
    # ============================================================
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Sistema Distribución y Logística")
    app.setOrganizationName("CodigoCritico")

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # ============================================================
    # 7. SPLASH DE INICIO
    # ============================================================
    splash = SplashScreenConAnimacion()
    splash.show()
    app.processEvents()
    print("✅ Splash de inicio mostrado")

    # ============================================================
    # 8. LOGIN Y VENTANA PRINCIPAL
    # ============================================================
    ventana = None

    def mostrar_login():
        nonlocal ventana
        splash.cerrar()

        db = obtener_conexion()
        login = DialogoLogin(db)

        if login.exec() == QDialog.DialogCode.Accepted:
            ventana = VentanaPrincipal(usuario=login.usuario_actual)
            ventana.show()
            ventana.raise_()
            ventana.activateWindow()
            ventana.setWindowState(ventana.windowState() & ~Qt.WindowState.WindowMinimized)
            ventana.repaint()
            QApplication.processEvents()
            print("✅ Ventana principal mostrada")
            print(f"📐 Escala aplicada: {factor_escala * 100}%")
        else:
            print("❌ Login cancelado. Saliendo...")
            app.quit()

    QTimer.singleShot(4000, mostrar_login)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()