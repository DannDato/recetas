from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class show_info(QWidget):
    def __init__(self, on_guardar_callback=None, receta_id=None, nombre="", instrucciones="", ingredientes=None):
        super().__init__()
        self.setWindowTitle("Acerca de esta app")
        self.setMinimumWidth(600)
        self.setWindowIcon(QIcon("img/icono.ico"))

        layout = QVBoxLayout()

        # Título principal
        titulo = QLabel("🍽️ Gestor de Recetas de Cocina")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 20px;
        """)
        layout.addWidget(titulo)

        # Subtítulo
        subtitulo = QLabel("Acerca de esta aplicación")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f0f0f0;
            margin-bottom: 8px;
        """)
        layout.addWidget(subtitulo)

        # Descripción justificada
        descripcion = QLabel("""
            <div style="text-align: justify;">
            Esta aplicación fue desarrollada para facilitar la gestión y consulta de recetas de cocina. 
            Podrás registrar recetas detalladas incluyendo sus ingredientes, cantidades, precios e instrucciones de preparación.

            Cuenta con funcionalidades avanzadas como búsqueda por ingredientes disponibles, sugerencias automáticas al escribir ingredientes, 
            y una interfaz simple pero potente para facilitar la navegación.

            </div>
        """)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("font-size: 14px; color: #dddddd;")
        layout.addWidget(descripcion)

        # Sección de detalles técnicos
        detalles = QLabel("""
            <b>Características destacadas:</b><br>
            • Registro completo de recetas<br>
            • Cálculo de costos por receta<br>
            • Sugerencias de ingredientes existentes<br>
            • Búsqueda por ingredientes con coincidencias parciales<br>
            • Almacenamiento local sin necesidad de conexión a internet
        """)
        detalles.setWordWrap(True)
        detalles.setStyleSheet("font-size: 13px; color: #cccccc; margin-top: 10px;")
        layout.addWidget(detalles)

        # Autor
        autor = QLabel("""
            <br>
            <div style="margin-top: 80px; font-size: 12px; color: #aaaaaa; text-align: center;">
            Desarrollado sin fines de lucro por <b>Alberto Daniel Tovar Mendoza</b><br>
            Todos los derechos reservados © 2025
            </div>
        """)
        autor.setWordWrap(True)
        layout.addWidget(autor)

        self.setLayout(layout)
