
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QCompleter, 
    QStyledItemDelegate,
    QHeaderView, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database.db_manager import obtener_todos_ingredientes

class FormularioNuevaReceta(QWidget):
    def __init__(self, on_guardar_callback=None, receta_id=None, nombre="", instrucciones="", ingredientes=None):
        super().__init__()
        self.setWindowTitle("Agregar nueva receta")
        self.setMinimumWidth(500)
        self.on_guardar_callback = on_guardar_callback
        self.receta_id = receta_id
        self.nombre = nombre
        self.instrucciones = instrucciones
        self.ingredientes = ingredientes or []

        layout = QVBoxLayout()


        self.setWindowIcon(QIcon("img/receta.ico"))

        if self.receta_id is None:
            self.titulo = QLabel("Nueva Receta... 😃")
        else:
            self.titulo = QLabel(f"{self.nombre} ... ✏️")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 15px;
        """)
        layout.addWidget(self.titulo)

        layout.addWidget(QLabel("Nombre de la receta:"))
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_input)

        layout.addWidget(QLabel("Instrucciones:"))
        self.instrucciones_input = QTextEdit()
        layout.addWidget(self.instrucciones_input)

        layout.addWidget(QLabel("Ingredientes:"))
        self.ingredientes_tabla = QTableWidget(0, 3)
        self.ingredientes_tabla.setHorizontalHeaderLabels(["Ingrediente", "Cantidad", "Precio"])
        # Obtener el header horizontal
        header = self.ingredientes_tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Columna 1 y 2 (Cantidad y Precio): tamaño fijo
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        # Asignar delegado con autocompletar a la columna 0 (Ingrediente)
        delegate = CompleterDelegate(self.ingredientes_tabla)
        
        self.ingredientes_tabla.setItemDelegateForColumn(0, delegate)

        layout.addWidget(self.ingredientes_tabla)

        # ------------------------------------------------------------------------------
        layout_botones = QHBoxLayout()  # Layout horizontal para botones
        boton_agregar_ingrediente = QPushButton("Agregar ingrediente")
        boton_agregar_ingrediente.clicked.connect(self.agregar_fila_ingrediente)

        boton_eliminar_ingrediente = QPushButton("Eliminar ingrediente")
        boton_eliminar_ingrediente.setProperty("clase", "eliminar")
        boton_eliminar_ingrediente.clicked.connect(self.eliminar_fila_ingrediente)

        # Agregas el layout horizontal al layout principal vertical
        layout_botones.addWidget(boton_eliminar_ingrediente)
        layout_botones.addWidget(boton_agregar_ingrediente)
        layout.addLayout(layout_botones)
        # ------------------------------------------------------------------------------



        boton_guardar = QPushButton("Guardar receta")
        boton_guardar.setProperty("clase", "guardar")
        boton_guardar.clicked.connect(self.guardar_receta)
        layout.addWidget(boton_guardar)


        self.setLayout(layout)
        # cargar datos si vienen
        self.nombre_input.setText(nombre)
        self.instrucciones_input.setPlainText(instrucciones)
        ingredientes = ingredientes or []
        for ing in ingredientes:
            self.agregar_fila_ingrediente()
            fila = self.ingredientes_tabla.rowCount() - 1
            self.ingredientes_tabla.setItem(fila, 0, QTableWidgetItem(ing[0]))  # Nombre ingrediente
            self.ingredientes_tabla.setItem(fila, 1, QTableWidgetItem(str(ing[1])))  # Cantidad
            self.ingredientes_tabla.setItem(fila, 2, QTableWidgetItem(str(ing[2])))  # Precio unitario


    def agregar_fila_ingrediente(self):
        fila = self.ingredientes_tabla.rowCount()
        self.ingredientes_tabla.insertRow(fila)

        self.ingredientes_tabla.setItem(fila, 0, QTableWidgetItem(""))  # Nombre

        cantidad_input = QTableWidgetItem("1")
        self.ingredientes_tabla.setItem(fila, 1, cantidad_input)

        precio_input = QTableWidgetItem("0.0")
        self.ingredientes_tabla.setItem(fila, 2, precio_input)

    def guardar_receta(self):
        nombre = self.nombre_input.text().strip()
        instrucciones = self.instrucciones_input.toPlainText().strip()

        if not nombre:
            QMessageBox.warning(self, "Error", "La receta debe tener un nombre.")
            return

        ingredientes = []
        for fila in range(self.ingredientes_tabla.rowCount()):
            item_nombre = self.ingredientes_tabla.item(fila, 0)
            item_cantidad = self.ingredientes_tabla.item(fila, 1)
            item_precio = self.ingredientes_tabla.item(fila, 2)

            if not item_nombre or not item_cantidad or not item_precio:
                continue

            nombre_ing = item_nombre.text().strip()
            cantidad = item_cantidad.text().strip()
            precio = item_precio.text().strip()

            if not nombre_ing or not cantidad:
                continue

            try:
                cantidad_val = float(cantidad)
                precio_val = float(precio)
            except ValueError:
                QMessageBox.warning(self, "Error", "Verifica que cantidad y precio sean números válidos.")
                return

            ingredientes.append((nombre_ing, cantidad_val, precio_val))

        if not ingredientes:
            QMessageBox.warning(self, "Error", "Debes agregar al menos un ingrediente.")
            return

        from database.db_manager import guardar_receta_completa, actualizar_receta_completa

        if self.receta_id is None:
            guardar_receta_completa(nombre, instrucciones, ingredientes)
        else:
            actualizar_receta_completa(self.receta_id, nombre, instrucciones, ingredientes)

        if self.on_guardar_callback:
            self.on_guardar_callback()
        self.close()


    def eliminar_fila_ingrediente(self):
        filas_seleccionadas = self.ingredientes_tabla.selectionModel().selectedRows()
        for fila in sorted(filas_seleccionadas, reverse=True):
            self.ingredientes_tabla.removeRow(fila.row())



class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        ingredientes = obtener_todos_ingredientes()
        self.completer = QCompleter(ingredientes)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)


    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setCompleter(self.completer)
        return editor