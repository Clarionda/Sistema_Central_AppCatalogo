"""
Código Crítico - Tercer Semestre Año 2026
Splash redondo con barra de progreso para aplicar escala
"""

import time
from PyQt6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QPixmap, QRegion, QLinearGradient


class SplashEscala(QSplashScreen):
    """Splash redondo con barra de progreso para aplicar escala."""

    def __init__(self, texto_inicial="Aplicando configuración...", parent=None):
        self.radius = 200
        self.angulo = 0
        self.progreso_valor = 0
        self.texto = texto_inicial

        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setMask(QRegion(0, 0, 400, 400, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.FramelessWindowHint |
                           Qt.WindowType.SplashScreen)

        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulo)
        self.timer_animacion.start(50)

        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso)

        self.show()
        QApplication.processEvents()

    def _actualizar_angulo(self):
        self.angulo = (self.angulo + 6) % 360
        self.update()

    def _actualizar_progreso(self):
        if self.progreso_valor < 100:
            self.progreso_valor += 1
            self.update()

    def iniciar_progreso(self, duracion_segundos=3):
        self.progreso_valor = 0
        paso_ms = max(1, int((duracion_segundos * 1000) // 100))
        self.timer_progreso.start(paso_ms)

    def set_texto(self, texto):
        self.texto = texto
        self.update()

    def set_progreso(self, valor):
        self.progreso_valor = min(valor, 100)
        self.update()
        QApplication.processEvents()

    def finalizar(self):
        self.timer_animacion.stop()
        self.timer_progreso.stop()
        self.progreso_valor = 100
        self.update()
        QApplication.processEvents()
        time.sleep(0.3)
        self.close()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 180

        gradiente = QLinearGradient(centro_x - radio, centro_y - radio,
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(1, QColor(13, 71, 161))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        pen = QPen()
        pen.setWidth(4)

        # Anillo 1
        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 140, centro_y - 140, 280, 280,
                       self.angulo * 16, 120 * 16)

        # Anillo 2
        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 120, centro_y - 120, 240, 240,
                       (360 - self.angulo) * 16, 90 * 16)

        # Anillo 3
        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 100, centro_y - 100, 200, 200,
                       (self.angulo + 180) * 16, 80 * 16)

        # Icono central
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

        # Texto
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(centro_x - 150, centro_y + 35, 300, 40),
                        Qt.AlignmentFlag.AlignCenter, self.texto)

        # Barra circular
        if self.progreso_valor > 0:
            pen.setWidth(6)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            angulo_fin = int(360 * self.progreso_valor / 100)
            painter.drawArc(centro_x - 85, centro_y - 85, 170, 170,
                          90 * 16, angulo_fin * 16)

            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.setPen(QColor(255, 193, 7))
            painter.drawText(QRect(centro_x - 50, centro_y - 25, 100, 50),
                            Qt.AlignmentFlag.AlignCenter, f"{self.progreso_valor}%")