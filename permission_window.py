from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QLabel, QPushButton
from PyQt6.QtCore import Qt

class PermisoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extraction permission")
        self.setModal(True)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # Mensaje
        mensaje = QLabel("To continue with data extraction, you must accept that permission has been granted to extract the data from the target profile.")
        mensaje.setWordWrap(True)
        layout.addWidget(mensaje)

        # Checkbox
        self.checkbox = QCheckBox("The target profile has given consent to extract their data.")
        layout.addWidget(self.checkbox)

        # Botón continuar (inicialmente deshabilitado)
        self.boton_continuar = QPushButton("Continue")
        self.boton_continuar.setEnabled(False)
        self.boton_continuar.clicked.connect(self.accept)
        layout.addWidget(self.boton_continuar)

        # Conexión para habilitar el botón solo si se marca la casilla
        self.checkbox.stateChanged.connect(self.toggle_boton)

    def toggle_boton(self, estado):
        self.boton_continuar.setEnabled(self.checkbox.isChecked())

