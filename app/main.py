"""
Código Crítico - Tercer Semestre - Año 2026
Punto de entrada principal de la aplicación.
Muestra splash de bienvenida, sincroniza datos, y luego el login.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from database import inicializar_base_datos
from sync import iniciar_hilo_sincronizacion
from ventana_login import LoginDialog
from ventana_principal import VentanaPrincipal
from splash import SplashBienvenida

def main():
    app = QApplication(sys.argv)
    
    # Inicializar base de datos
    inicializar_base_datos()
    
    # Variable para mantener la ventana principal
    ventana_principal = None
    
    def mostrar_login():
        nonlocal ventana_principal
        login = LoginDialog()
        if login.exec():
            # Login exitoso - crear y mostrar ventana principal
            ventana_principal = VentanaPrincipal()
            ventana_principal.show()
        else:
            # Login cancelado - salir
            sys.exit(0)
    
    # Mostrar splash y conectar con login
    splash = SplashBienvenida()
    splash.terminado.connect(mostrar_login)
    
    # Iniciar hilo de sincronización (solo después de que el splash termine)
    # Lo hacemos en mostrar_login() o aquí con un timer
    def iniciar_sync():
        iniciar_hilo_sincronizacion()
    
    splash.terminado.connect(iniciar_sync)
    
    # Ejecutar bucle principal
    sys.exit(app.exec())

if __name__ == "__main__":
    main()