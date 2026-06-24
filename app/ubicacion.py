import uuid
from PyQt6.QtCore import QObject, QTimer
from database import ejecutar_consulta
from auth import obtener_preventista_id

# Importación condicional de QtPositioning
try:
    from PyQt6.QtPositioning import QGeoPositionInfoSource
    GPS_DISPONIBLE = True
except ImportError:
    GPS_DISPONIBLE = False
    print("Advertencia: QtPositioning no disponible. El GPS no funcionará.")

class RastreadorUbicacion(QObject):
    def __init__(self):
        super().__init__()
        self.source = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.obtener_y_guardar_posicion)
        self.timer.start(30000)
        if GPS_DISPONIBLE:
            self.iniciar_gps()
        else:
            print("GPS desactivado (módulo QtPositioning no encontrado)")

    def iniciar_gps(self):
        self.source = QGeoPositionInfoSource.createDefaultSource(self)
        if self.source:
            self.source.positionUpdated.connect(self.guardar_posicion)
            self.source.startUpdates()
            print("GPS iniciado")
        else:
            print("No se pudo iniciar GPS (sin hardware o permisos)")

    def guardar_posicion(self, info):
        if not GPS_DISPONIBLE:
            return
        coord = info.coordinate()
        if coord.isValid():
            lat = coord.latitude()
            lon = coord.longitude()
            preventista_id = obtener_preventista_id()
            if preventista_id:
                id_pos = str(uuid.uuid4())
                ejecutar_consulta("""
                    INSERT INTO posiciones_preventistas (id, preventista_id, latitud, longitud, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (id_pos, preventista_id, lat, lon), commit=True)
                print(f"Posición guardada: {lat}, {lon}")

    def obtener_y_guardar_posicion(self):
        if GPS_DISPONIBLE and self.source:
            self.source.requestUpdate()

    def obtener_ultima_posicion(self):
        filas = ejecutar_consulta("SELECT latitud, longitud FROM posiciones_preventistas ORDER BY created_at DESC LIMIT 1")
        if filas:
            return filas[0]["latitud"], filas[0]["longitud"]
        return None, None

def registrar_visita_cliente(cliente_id):
    from auth import obtener_usuario_actual
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    preventista_id = usuario.get("preventista_id")
    if not preventista_id:
        return
    id_visita = str(uuid.uuid4())
    lat, lon = None, None
    if hasattr(registrar_visita_cliente, "rastreador"):
        lat, lon = registrar_visita_cliente.rastreador.obtener_ultima_posicion()
    ejecutar_consulta("""
        INSERT INTO visitas_clientes (id, preventista_id, cliente_id, fecha_hora, latitud, longitud, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, CURRENT_TIMESTAMP)
    """, (id_visita, preventista_id, cliente_id, lat, lon), commit=True)
    print(f"Visita registrada: cliente {cliente_id} por preventista {preventista_id}")