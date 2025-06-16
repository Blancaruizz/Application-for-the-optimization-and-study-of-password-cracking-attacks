from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout, QMessageBox
import os
from styles import Styles

'''
Class for opening the dictionarios in a pop-up window to view/edit them.
'''
class WindowDictionary(QWidget):
    def __init__(self, file):
        super().__init__()
        self.file = os.path.join("dictionaries", file)
        self.setWindowTitle(f"Dictionary: {file}")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet("background-color: #B7B2B2;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(Styles.text_edit())
        layout.addWidget(self.text_edit)

        self.modify_button = QPushButton("Modify Dictionary ✏️", self)
        self.modify_button.clicked.connect(self.enable_editing)
        layout.addWidget(self.modify_button)

        button_layout = QHBoxLayout()
        self.accept_button = QPushButton("Accept ✔", self)
        self.accept_button.clicked.connect(self.save_changes)
        self.accept_button.setVisible(False)

        self.cancel_button = QPushButton("Cancel ❌", self)
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setVisible(False)

        button_layout.addStretch()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.modify_button.setStyleSheet(Styles.button_general())
        self.accept_button.setStyleSheet(Styles.button_general())
        self.cancel_button.setStyleSheet(Styles.button_general())

        self.load_dictionary()

    def load_dictionary(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                self.text_edit.setPlainText(f.read())
        except FileNotFoundError:
            self.text_edit.setPlainText(f"The file '{self.file}' does not exist.")

    def enable_editing(self):
        self.text_edit.setReadOnly(False)
        self.modify_button.setVisible(False)
        self.accept_button.setVisible(True)
        self.cancel_button.setVisible(True)

    def save_changes(self):
        with open(self.file, "w", encoding="utf-8") as f:
            f.write(self.text_edit.toPlainText())
        self.text_edit.setReadOnly(True)
        self.modify_button.setVisible(True)
        self.accept_button.setVisible(False)
        self.cancel_button.setVisible(False)

        # Mostrar mensaje de confirmación
        QMessageBox.information(self, "Saved", "The changes have been saved successfully.")
