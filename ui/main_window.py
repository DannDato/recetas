from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QToolButton, 
    QLineEdit, QHBoxLayout, QListWidgetItem, QMessageBox
)
from PyQt6.QtGui import QIcon, QColor, QBrush, QFont
from PyQt6.QtCore import QSize, Qt

from database.db_manager import (
    obtener_recetas, obtener_receta, eliminar_receta_por_id
)
from ui.nueva_receta import FormularioNuevaReceta
from ui.info import show_info



class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recetas")
        self.setGeometry( 750, 250, 500, 500)
        self.layout = QVBoxLayout()

        self.setWindowIcon(QIcon("img/icono.ico"))

        self.titulo = QLabel("Mis Recetas 🍽️")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 0px -50px 15px 0px;
        """)

        self.lista_recetas = QListWidget()
        self.boton_agregar = QPushButton("Nueva receta")
        self.boton_agregar.clicked.connect(self.abrir_formulario_nueva_receta)

        # Barra de búsqueda
        self.busqueda_ingredientes_input = QLineEdit()
        self.busqueda_ingredientes_input.setPlaceholderText("Buscar por ingredientes (separados por coma)")
        self.busqueda_ingredientes_input.textChanged.connect(self.buscar_por_ingredientes)

        # Crear botón limpiar
        self.clear_button = QToolButton()
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))  # icono estándar, si no funciona, puedes usar un icono custom o texto
        self.clear_button.setIconSize(QSize(12, 12))
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setToolTip("Limpiar búsqueda")
        self.clear_button.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self.clear_button.clicked.connect(lambda: self.busqueda_ingredientes_input.clear())

        # Layout horizontal para input + boton
        layout_busqueda = QHBoxLayout()
        layout_busqueda.addWidget(self.busqueda_ingredientes_input)
        layout_busqueda.addWidget(self.clear_button)

        self.boton_eliminar = QPushButton("Eliminar receta")
        self.boton_eliminar.setProperty("clase", "eliminar")
        self.boton_eliminar.clicked.connect(self.eliminar_receta_seleccionada)

        self.info_button = QToolButton()
        self.info_button.setIconSize(QSize(15, 15))
        self.info_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_button.setToolTip("Información")
        self.info_button.setIcon(QIcon.fromTheme("help-about"))  # icono estándar, si no funciona, puedes usar un icono custom o texto
        self.info_button.setStyleSheet("QToolButton { border: none; padding: 3px; margin:5px }")
        self.info_button.clicked.connect(self.show_info)

        # Agregar widgets y layout de búsqueda
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.titulo)
        title_layout.addWidget(self.info_button) 
        self.layout.addLayout(title_layout)
        self.layout.addWidget(self.lista_recetas)
        self.layout.insertLayout(2, layout_busqueda)
        botones_layout = QHBoxLayout()

        botones_layout.addWidget(self.boton_eliminar)
        botones_layout.addWidget(self.boton_agregar)
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

        self.cargar_recetas()
        self.lista_recetas.itemDoubleClicked.connect(self.editar_receta)


    
    def cargar_recetas(self):
        self.lista_recetas.clear()
        recetas = obtener_recetas()
        fuente = QFont("Courier New")
        fuente.setPointSize(12)

        MAX_LEN = 30

        for index, receta in enumerate(recetas, start=1):
            receta_id, nombre, costo = receta

            # Recorta el nombre si es muy largo
            nombre_recortado = nombre
            if len(nombre) > MAX_LEN:
                nombre_recortado = nombre[:MAX_LEN - 2] + "…"

            texto_item = f"{index:>2}. {nombre_recortado.ljust(MAX_LEN)}  ${costo:6.2f}"

            item = QListWidgetItem(texto_item)
            item.setFont(fuente)
            item.setData(256, receta_id)
            self.lista_recetas.addItem(item)



    def abrir_formulario_nueva_receta(self):
        self.formulario = FormularioNuevaReceta(on_guardar_callback=self.cargar_recetas)
        self.formulario.show()
    
    def show_info(self):
        self.info_window = show_info()
        self.info_window.show()

    def editar_receta(self, item):
        receta_id = item.data(256) 
        if receta_id is None:
            return
        receta = obtener_receta(receta_id)
        if receta:
            self.formulario = FormularioNuevaReceta(
                on_guardar_callback=self.cargar_recetas,
                receta_id=receta['id'],
                nombre=receta['nombre'],
                instrucciones=receta['instrucciones'],
                ingredientes=receta['ingredientes']
            )
            self.formulario.show()


    def buscar_por_ingredientes(self):
        texto = self.busqueda_ingredientes_input.text().strip()
        if not texto:
            self.cargar_recetas()  # carga todas si está vacío
            return

        ingredientes = [i.strip().lower() for i in texto.split(",") if i.strip()]

        from database.db_manager import buscar_recetas_por_ingredientes
        recetas = buscar_recetas_por_ingredientes(ingredientes)

        self.lista_recetas.clear()
        for receta in recetas:
            porcentaje = receta.get('porcentaje_coincidencia', 0)
            texto_item = f"{receta['nombre']} ({porcentaje*100:.0f}%)"
            item = QListWidgetItem(texto_item)
            item.setData(256, receta['id']) 

            # Colorea rojo si < 70%
            if porcentaje < 0.7:
                item.setForeground(QBrush(QColor("red")))
            elif porcentaje < 0.9 and porcentaje >= 0.7:
                # Colorea amarillo si entre 70% y 90%
                item.setForeground(QBrush(QColor("yellow")))
            elif porcentaje >= 0.9:
                item.setForeground(QBrush(QColor("green")))
            else:
                item.setForeground(QBrush(QColor("white")))

            self.lista_recetas.addItem(item)

    def eliminar_receta_seleccionada(self):
        item = self.lista_recetas.currentItem()
        if not item:
            QMessageBox.information(self, "Sin selección", "Selecciona una receta para eliminar.")
            return

        texto = item.text()
        receta_id = item.data(Qt.ItemDataRole.UserRole)

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que quieres eliminar la receta:\n\n{texto}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            eliminar_receta_por_id(receta_id)
            self.cargar_recetas()
