"""
Código Crítico - Tercer Semestre - Año 2026
Ventana principal de la aplicación (preventista).
Muestra un mapa interactivo con los clientes asignados al preventista logueado.
Permite sincronizar manualmente y cerrar sesión.
Incluye modo kiosco (pantalla completa) y rastreador GPS opcional.
"""

import sys
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QStatusBar, QMessageBox, QHBoxLayout, QLabel, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeyEvent
from database import ejecutar_consulta
from sync import sincronizacion_completa
from auth import obtener_usuario_actual, cerrar_sesion
from ventana_catalogo import CatalogoDialog

try:
    from ubicacion import RastreadorUbicacion, registrar_visita_cliente
    GPS_DISPONIBLE = True
except ImportError:
    GPS_DISPONIBLE = False
    def registrar_visita_cliente(cliente_id):
        pass
    class RastreadorUbicacion:
        def __init__(self):
            print("GPS no disponible")
        def obtener_ultima_posicion(self):
            return None, None

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distribuidora - Preventista")
        
        # Modo kiosco: pantalla completa, sin bordes
        self.showFullScreen()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.usuario = obtener_usuario_actual()
        if not self.usuario:
            self.close()
            return
        
        # Debug: ver qué usuario está logueado
        print(f"[DEBUG] Usuario logueado: {self.usuario}")
        print(f"[DEBUG] preventista_id: {self.usuario.get('preventista_id')}")

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Barra superior con botones
        top = QHBoxLayout()
        top.setSpacing(20)
        
        self.lbl_usuario = QLabel(f"Usuario: {self.usuario['username']} ({self.usuario['rol']})")
        self.lbl_usuario.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        # Botón sincronizar
        btn_sync = QPushButton("🔄 Sincronizar ahora")
        btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sync.setMinimumHeight(45)
        btn_sync.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_sync.clicked.connect(self.sincronizar_manual)
        
        # Botón nuevo cliente
        btn_nuevo_cliente = QPushButton("➕ Nuevo Cliente")
        btn_nuevo_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nuevo_cliente.setMinimumHeight(45)
        btn_nuevo_cliente.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        btn_nuevo_cliente.clicked.connect(self.agregar_cliente)
        
        # Botón cerrar sesión
        btn_logout = QPushButton("🚪 Cerrar sesión")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setMinimumHeight(45)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_logout.clicked.connect(self.logout)
        
        top.addWidget(self.lbl_usuario)
        top.addStretch()
        top.addWidget(btn_sync)
        top.addWidget(btn_nuevo_cliente)
        top.addWidget(btn_logout)
        layout.addLayout(top)

        # WebView para el mapa
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        self.statusBar().showMessage("Listo")
        self.actualizar_mapa()

        # Timer para detectar clics en los marcadores del mapa
        self.timer_marker = QTimer()
        self.timer_marker.timeout.connect(self.verificar_marker_click)
        self.timer_marker.start(500)

        # Iniciar rastreador de ubicación (GPS) si está disponible
        if GPS_DISPONIBLE:
            self.rastreador = RastreadorUbicacion()
            registrar_visita_cliente.rastreador = self.rastreador
        else:
            self.rastreador = None

    def actualizar_mapa(self):
        """Actualiza el mapa con los clientes que tienen coordenadas y están asignados al preventista logueado."""
        usuario = self.usuario
        
        # Si el usuario es admin, ver todos los clientes
        if usuario.get('rol') == 'admin':
            clientes = ejecutar_consulta("SELECT id, razon_social, latitud, longitud FROM clientes WHERE latitud IS NOT NULL AND longitud IS NOT NULL")
            print(f"[DEBUG] Admin: Mostrando {len(clientes)} clientes")
        else:
            # Obtener el preventista_id del usuario logueado
            preventista_id = usuario.get('preventista_id')
            if not preventista_id:
                self.statusBar().showMessage("Usuario no tiene preventista asignado")
                print("[DEBUG] ERROR: Usuario sin preventista_id")
                return
            
            # Filtrar clientes por preventista_id
            clientes = ejecutar_consulta(
                "SELECT id, razon_social, latitud, longitud FROM clientes WHERE preventista_id = ? AND latitud IS NOT NULL AND longitud IS NOT NULL",
                (preventista_id,)
            )
            print(f"[DEBUG] Preventista {preventista_id}: Mostrando {len(clientes)} clientes")

        # Generar HTML con Leaflet
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
            <title>Mapa de Clientes</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { height: 100%; width: 100%; position: absolute; top: 0; left: 0; }
                body { margin: 0; padding: 0; }
                .leaflet-popup-content { font-size: 16px; }
                button { font-size: 16px; padding: 8px 16px; background-color: #3498db; color: white; border: none; border-radius: 8px; cursor: pointer; }
                button:hover { background-color: #2980b9; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([-38.4161, -63.6167], 5);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                }).addTo(map);
        """
        for c in clientes:
            html += f"""
                var marker = L.marker([{c['latitud']}, {c['longitud']}]).addTo(map);
                marker.bindPopup("<b>{c['razon_social']}</b><br><button onclick='window.triggerMarkerClick({c["id"]})'>Ver catálogo</button>");
            """
        html += """
                window.triggerMarkerClick = function(cliente_id) {
                    window.clienteSeleccionado = cliente_id;
                };
            </script>
        </body>
        </html>
        """
        self.webview.setHtml(html)

    def verificar_marker_click(self):
        """Verifica si se hizo clic en un marcador del mapa."""
        self.webview.page().runJavaScript("window.clienteSeleccionado", self.procesar_cliente_seleccionado)

    def procesar_cliente_seleccionado(self, cliente_id):
        """Procesa el clic en un marcador y abre el catálogo del cliente."""
        if cliente_id and int(cliente_id) > 0:
            self.webview.page().runJavaScript("window.clienteSeleccionado = null;")
            cliente = ejecutar_consulta("SELECT razon_social FROM clientes WHERE id = ?", (int(cliente_id),))
            if cliente:
                dialog = CatalogoDialog(int(cliente_id), cliente[0]['razon_social'], self)
                dialog.exec()

    def sincronizar_manual(self):
        """Fuerza la sincronización manual con Turso."""
        self.statusBar().showMessage("Sincronizando...")
        try:
            sincronizacion_completa()
            self.statusBar().showMessage("Sincronización completada", 3000)
            self.actualizar_mapa()  # Recargar mapa por si hay nuevos clientes
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en sincronización: {e}")
            self.statusBar().showMessage("Error en sincronización")

    def agregar_cliente(self):
        """Abre el diálogo para agregar un nuevo cliente."""
        from ventana_nuevo_cliente import NuevoClienteDialog
        dialog = NuevoClienteDialog(self)
        if dialog.exec():
            self.actualizar_mapa()
            self.statusBar().showMessage("Cliente agregado. Se sincronizará automáticamente.", 3000)

    def logout(self):
        """Cierra la sesión actual y cierra la ventana."""
        cerrar_sesion()
        self.close()
        QApplication.quit()

    def keyPressEvent(self, event: QKeyEvent):
        """Permite cerrar la aplicación con Ctrl+Q (modo kiosco)."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.close()
            QApplication.quit()
        super().keyPressEvent(event)