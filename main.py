import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from database import init_db
from ui.main_window import VentanaPrincipal

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)

    # Cargar QSS
    qss_path = resource_path("style/style.qss")
    with open(qss_path, "r") as f:
        app.setStyleSheet(f.read())

    # Icono global
    app.setWindowIcon(QIcon(resource_path("img/icono.ico")))

    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
