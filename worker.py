from PyQt6.QtCore import QThread, pyqtSignal
from john_reaper import JohnTheRipperProcessor
from gemini import GeminiProcessor

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Clases para ejecutar los programas mientras se muestra una ventana de "cargando"

class JohnWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, diccionario, profile, modo):
        super().__init__()
        self.diccionario = diccionario
        self.profile = profile
        self.modo = modo

    def run(self):
        john_processor = JohnTheRipperProcessor()
        resultado = john_processor.run_john(self.diccionario, self.profile, self.modo)
        self.finished.emit(resultado)

class ProgresoJohnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cracking password...")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setFixedSize(300, 200)

        self.setStyleSheet("""
            QDialog {
                background-color: #EDEDED;
                border: 2px solid #35308F;
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                color: #35308F;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_texto = QLabel("Running John the Ripper...", self)
        self.label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_texto)

        self.spinner_label = QLabel(self)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("assets/spinner.gif")
        self.spinner_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.spinner_label)

class GeminiWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, dictionary, modo):
        super().__init__()
        self.dictionary = dictionary
        self.modo = modo
        self.gemini_processor = GeminiProcessor()  

    def run(self):
        try:
            if self.modo == "expand":
                result = self.gemini_processor.extend_dictionary(self.dictionary)
            elif self.modo == "reduce":
                result = self.gemini_processor.reduce_dictionary(self.dictionary)
            else:
                result = ""
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in GeminiWorker ({self.modo}):", e)
            self.finished.emit("")
