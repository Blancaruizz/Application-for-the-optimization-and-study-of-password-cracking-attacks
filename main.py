import sys
import os
from PyQt6.QtWidgets import QTextEdit, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QComboBox, QLineEdit, QDialog, QLabel, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer

from crawler_module import DataExtractor
from open_window import WindowDictionary
from worker import JohnWorker, GeminiWorker, ProgresoJohnDialog
from permission_window import PermisoDialog
from playwright.sync_api import sync_playwright
from styles import Styles


class GUIModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TFG - JOHN THE RIPPER")
        self.setGeometry(100, 100, 600, 400)

        # Initialize variables to control the data extraction process
        self.counter_recents = 0  # Counter for recent posts
        self.counter_old = 0   # Counter for old posts
        self.output = [] # List to store the words to be saved in the target profile dictionary
        self.recent = True # Boolean flag to indicate whether to extract recent or old posts
        self.activate_avoid_overloading = False # Control flag for old posts extraction when profile has many posts
        self.counter_scroll = 0 # Total number of scrolls performed during data extraction

        # Initialize the GUI elements
        self.init_ui()

    def init_ui(self):
        # Set up the main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #B7B2B2;")

        main_layout = QVBoxLayout(self.central_widget)

        # ---------- Top right: UC3M logo ----------
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()

        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo_uc3m.png")
        logo_pixmap = logo_pixmap.scaled(
            150, 50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(logo_layout)

        # ---------- Center title ----------
        title_label = QLabel("TFG JOHN THE RIPPER")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # ---------- Spacer (top) ----------
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        # Configure button size
        button_width = 200
        button_height = 100

        # ---------- Grid layout for main menu buttons ----------
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Button to start the data extraction process
        self.extract_button = QPushButton("Data Extraction", self)
        self.extract_button.setStyleSheet(Styles.button_general())
        self.extract_button.setFixedSize(button_width, button_height)
        self.extract_button.clicked.connect(self.start_extraction)
        grid_layout.addWidget(self.extract_button, 0, 0)

        # Button to consult and modify existing dictionaries
        self.dictionaries_button = QPushButton("Consult/Modify\nAvailable Dictionaries", self)
        self.dictionaries_button.setStyleSheet(Styles.button_general())
        self.dictionaries_button.setFixedSize(button_width, button_height)
        self.dictionaries_button.clicked.connect(self.open_dictionaries)
        grid_layout.addWidget(self.dictionaries_button, 0, 1)

        # Button to interact with the Gemini API for dictionary expansion/reduction
        self.chatgpt_button = QPushButton("Interact with Gemini", self)
        self.chatgpt_button.setStyleSheet(Styles.button_general())
        self.chatgpt_button.setFixedSize(button_width, button_height)
        self.chatgpt_button.clicked.connect(self.interact_gemini)
        grid_layout.addWidget(self.chatgpt_button, 1, 0)

        # Button to launch John the Ripper for password cracking
        self.john_button = QPushButton("Run John the Ripper", self)
        self.john_button.setStyleSheet(Styles.button_general())
        self.john_button.setFixedSize(button_width, button_height)
        self.john_button.clicked.connect(self.execute_john)
        grid_layout.addWidget(self.john_button, 1, 1)

        # ---------- Center the button grid in the window ----------
        grid_wrapper = QHBoxLayout()
        grid_wrapper.addStretch()
        grid_wrapper.addLayout(grid_layout)
        grid_wrapper.addStretch()

        main_layout.addLayout(grid_wrapper)

        # ---------- Spacer (bottom) ----------
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

############################################################
############# VIEW/MODIFY DICTIONARIES #####################
############################################################
    def open_dictionaries(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #B7B2B2;")

        # Main layout configuration
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ---------- Top layout with Back button and Logo ----------
        top_layout = QHBoxLayout()

        # Back button
        self.back_button = QPushButton("⬅ Back", self)
        self.back_button.setStyleSheet(Styles.button_general())
        self.back_button.clicked.connect(self.return_main_menu)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Spacer to center the logo to the right
        top_layout.addStretch()

        # UC3M logo in the upper right corner
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo_uc3m.png")
        logo_pixmap = logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        top_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(top_layout)

        # ---------- Section title ----------
        label = QLabel("Select the dictionary you want to consult or modify:")
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        main_layout.addWidget(label)

        # ---------- List available dictionaries ---------
        folder = "dictionaries"
        if not os.path.exists(folder):
            os.makedirs(folder)

        files = [f for f in os.listdir(folder) if f.endswith(".txt")]

        if files:
            # For each dictionary file, create a button to open it
            for file in files:
                button = QPushButton(file, self)
                button.clicked.connect(lambda checked, file=file: self.show_dictionary(file))
                button.setStyleSheet(Styles.button_general())
                button.setFixedHeight(40)
                main_layout.addWidget(button)
        else:
            # If no dictionary files are found, display a warning message
            no_files_label = QLabel("There are no dictionaries available.", self)
            no_files_label.setStyleSheet("color: red; font-size: 14px;")
            main_layout.addWidget(no_files_label)
##################################################################

##################################################################
############### INTERACT WITH GEMINI #############################
##################################################################
    def interact_gemini(self):
        '''Displays the UI to select a dictionary and trigger its expansion or reduction with Gemini.'''
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #B7B2B2;")

        # Main layout configuration
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ---------- Top layout with Back button and Logo ----------
        top_layout = QHBoxLayout()

        self.back_button = QPushButton("⬅ Back", self)
        self.back_button.setStyleSheet(Styles.button_general())
        self.back_button.clicked.connect(self.return_main_menu)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        top_layout.addStretch()

        # UC3M logo in the upper right corner
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo_uc3m.png")
        logo_pixmap = logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        top_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)

        # ---------- Section title ----------
        title = QLabel("Select the dictionary you want to expand or reduce")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: black; margin-top: 10px;")
        main_layout.addWidget(title)

        # ---------- Selected dictionary label ----------
        self.label_diccionario = QLabel("No dictionary selected 🔍", self)
        self.label_diccionario.setStyleSheet("font-size: 14px; font-style: italic; color: #333333;")
        main_layout.addWidget(self.label_diccionario)

        # Dropdown menu
        self.combo_dictionaries = QComboBox(self)
        self.combo_dictionaries.setStyleSheet(Styles.combo_box())
        folder = "dictionaries"
        files = [f for f in os.listdir(folder) if f.endswith(".txt")]

        if files:
            self.combo_dictionaries.addItems(files)
            self.combo_dictionaries.currentTextChanged.connect(self.select_dictionary)
            self.select_dictionary(files[0])
            main_layout.addWidget(self.combo_dictionaries)
        else:
            main_layout.addWidget(QLabel("There are no available dictionaries.", self))
            return

        # ---------- Loading spinner (hidden by default) ----------
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_movie = QMovie("assets/spinner.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setVisible(False)
        main_layout.addWidget(self.loading_label)

        self.loading_text = QLabel("", self)
        self.loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_text.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.loading_text.setVisible(False)
        main_layout.addWidget(self.loading_text)

        # ---------- Action buttons (Expand / Reduce) ----------
        btn_layout = QHBoxLayout()

        # Button to expand dictionary with Gemini
        btn_expand = QPushButton("Expand dictionary with Gemini", self)
        btn_expand.setStyleSheet(Styles.expand_gemini())
        btn_expand.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_expand.clicked.connect(self.execute_gemini)
        btn_layout.addWidget(btn_expand)

        # Button to reduce dictionary with Gemini
        btn_reduce = QPushButton("Reduce dictionary with Gemini", self)
        btn_reduce.setStyleSheet(Styles.reduce_gemini())
        btn_reduce.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_reduce.clicked.connect(self.execute_reduction)
        btn_layout.addWidget(btn_reduce)

        main_layout.addLayout(btn_layout)

    def execute_gemini(self):
        '''Expands the selected dictionary by sending its content to Gemini for contextual enrichment.'''
        if not self.dictionary_selected:
            QMessageBox.warning(self, "Caution", "Select a dictionary before continuing.")
            return
        # Show loading spinner and message
        self.loading_label.setVisible(True)
        self.loading_text.setVisible(True)
        self.loading_movie.start()

        # Launch a background worker thread to expand the dictionary
        self.gemini_worker = GeminiWorker(self.dictionary_selected, modo="expand")
        self.gemini_worker.finished.connect(self.gemini_result)
        self.gemini_worker.start()

    def execute_reduction(self):
        '''Reduces the selected dictionary by removing irrelevant words via Gemini.'''
        if not self.dictionary_selected:
            QMessageBox.warning(self, "Caution", "Select a dictionary before continuing.")
            return
        # Show loading spinner and reduction message
        self.loading_label.setVisible(True)
        self.loading_text.setText("Deleting irrelevant words...")
        self.loading_text.setVisible(True)
        self.loading_movie.start()

        # Launch a background worker thread to reduce the dictionary
        self.delete_worker = GeminiWorker(self.dictionary_selected, modo="reduce")
        self.delete_worker.finished.connect(self.gemini_result)
        self.delete_worker.start()

    def gemini_result(self, result):
        '''Displays the result of the dictionary processing after expansion or reduction.'''
        # Stop the spinner and hide loading UI
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.loading_text.setVisible(False)
        # Notify the user of the output
        if result:
            QMessageBox.information(self, "Success", f" Dictionary modified: {result}")
        else:
            QMessageBox.warning(self, "Error", " It was not possible to modify the dictionary.")
##################################################################

##################################################################
############### JOHN THE RIPPER EXECUTION  #######################
##################################################################
    def execute_john(self):
        '''Displays the UI for running John the Ripper with selected attack modes and selected dictionary.'''
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #B7B2B2;")
        # Main layout configuration
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ---------- Top layout (Back button + UC3M Logo) ----------
        top_layout = QHBoxLayout()

        self.back_button = QPushButton("⬅ Back", self)
        self.back_button.setStyleSheet(Styles.button_general())
        self.back_button.clicked.connect(self.return_main_menu)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        top_layout.addStretch()

        # Logo UC3M
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo_uc3m.png")
        logo_pixmap = logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        top_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)

        # ---------- Section title ----------
        title = QLabel("🔐 Run John the Ripper")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: black;")
        main_layout.addWidget(title)

        # ---------- Selected dictionary label ----------
        self.label_diccionario = QLabel("No dictionary selected 📂", self)
        self.label_diccionario.setStyleSheet("font-size: 14px; font-style: italic; color: #333;")
        main_layout.addWidget(self.label_diccionario)

        # ---------- Dictionary dropdown menu ----------
        self.combo_dictionaries = QComboBox(self)
        self.combo_dictionaries.setStyleSheet(Styles.combo_box())
        folder = "dictionaries"
        files = [f for f in os.listdir(folder) if f.endswith(".txt")]

        if files:
            self.combo_dictionaries.addItems(files)
            self.combo_dictionaries.currentTextChanged.connect(self.select_dictionary)
            self.select_dictionary(files[0])
            main_layout.addWidget(self.combo_dictionaries)
        else:
            main_layout.addWidget(QLabel("There are no availale dictionaries.📂", self))
            return

        # ---------- Attack modes label + Help button ----------
        modos_layout = QHBoxLayout()
        modos_label = QLabel("⚔️ Select an attack mode:")
        modos_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 20px;")
        modos_layout.addWidget(modos_label, alignment=Qt.AlignmentFlag.AlignLeft)
        modos_layout.addStretch()

        help_layout = QHBoxLayout()

        # Button with help icon
        help_button = QPushButton("Help ❓", self)
        help_button.setStyleSheet(Styles.button_general())
        help_button.clicked.connect(self.show_help_john)
        help_layout.addWidget(help_button)

        modos_layout.addLayout(help_layout)
        main_layout.addLayout(modos_layout)

        # ---------- Attack mode buttons ----------
        botones_layout = QHBoxLayout()

        simple_btn = QPushButton("Simple Mode", self)
        simple_btn.setStyleSheet(Styles.simple_mode())
        simple_btn.clicked.connect(lambda: self.run_john("simple"))
        botones_layout.addWidget(simple_btn)

        medio_btn = QPushButton("Intermediate Mode", self)
        medio_btn.setStyleSheet(Styles.intermediate_mode())
        medio_btn.clicked.connect(lambda: self.run_john("intermediate"))
        botones_layout.addWidget(medio_btn)

        avanzado_btn = QPushButton("Advanced Mode", self)
        avanzado_btn.setStyleSheet(Styles.advanced_mode())
        avanzado_btn.clicked.connect(lambda: self.run_john("advanced"))
        botones_layout.addWidget(avanzado_btn)

        main_layout.addLayout(botones_layout)
    
    def select_dictionary(self, file):
        '''Updates the selected dictionary used for the attack.'''
        self.file = file
        self.dictionary_selected = os.path.join("dictionaries", file)
        self.label_diccionario.setText(f"Dictionary selected: {file}")

    def run_john(self, modo):
        '''Runs John the Ripper in a background thread with the selected attack mode.'''
        if not self.dictionary_selected:
            QMessageBox.warning(self, "Caution", "Select a dictionary before running John the Ripper.")
            return

        # Show progress dialog (spinner) during execution
        self.progreso_dialog = ProgresoJohnDialog(self)
        self.progreso_dialog.show()

        # Launch background worker thread to execute John the Ripper
        self.john_worker = JohnWorker(self.dictionary_selected, self.file, modo)
        self.john_worker.finished.connect(self.show_result)
        self.john_worker.start()
    
    def show_result(self, resultado):
        '''Displays the result of the password cracking operation.'''
        self.progreso_dialog.close() # Close progress dialog

        # Create custom window to display result and additional button
        dialog = QDialog(self)
        dialog.setWindowTitle("John the Ripper result")
        dialog.setFixedSize(500, 250)

        layout = QVBoxLayout()

        # Result text
        resultado_label = QLabel(resultado)
        resultado_label.setWordWrap(True)
        layout.addWidget(resultado_label)

        # Button to consult statistics
        stats_button = QPushButton("Check Statistics 📊", self)
        stats_button.setStyleSheet(Styles.button_general())
        stats_button.clicked.connect(self.show_statistics_john)
        layout.addWidget(stats_button)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()
    
    def show_statistics_john(self):
        '''Displays the statistics of the attack after John the Ripper execution.'''
        try:
            with open("statistics/statistics_" + self.file, "r", encoding="utf-8") as f:
                contenido = f.read()
        except FileNotFoundError:
            contenido = "The results file was not found."

        # Window to display the contents of the file
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("John the Ripper Statistics")
        stats_dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setPlainText(contenido)
        layout.addWidget(text_area)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(stats_dialog.close)
        layout.addWidget(close_button)

        stats_dialog.setLayout(layout)
        stats_dialog.exec()

    def show_help_john(self):
        '''Displays a help message explaining the available attack modes.'''
        texto_ayuda = (
            "<b>Simple Mode:</b> Uses only the dictionary, without applying any rule.<br><br>"
            "<b>Intermediate Mode:</b> Uses the dictionary combined with the default 'Jumbo' rules included with John the Ripper.<br><br>"
            "<b>Advanced Mode:</b> Uses the dictionary combined with 'InstagramRules' rules. This set of rules has been created in john.conf to exploit patterns observed in Instagram profile data.<br><br>"
            "⚠️ More advanced modes take longer to execute but have a higher success rate. ⚠️"
        )

        QMessageBox.information(self, "Help: Attack Modes", texto_ayuda)

####################################################################

##################################################################
########## DATA EXTRACTION #######################################
##################################################################
    def start_extraction(self):
        '''Displays the UI for starting the Data Extraction process'''
        # Start Playwright and open Chromium browser (visible)
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #B7B2B2;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # ---------- Top layout (Back button + UC3M Logo) ----------
        top_layout = QHBoxLayout()

        self.back_button = QPushButton("⬅ Back", self)
        self.back_button.setStyleSheet(Styles.button_general())
        self.back_button.clicked.connect(self.return_main_menu)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        top_layout.addStretch()

        # Logo UC3M
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo_uc3m.png")
        logo_pixmap = logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        top_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addLayout(top_layout)

        # ---------- Instructions ----------
        self.instruction_label = QLabel("Enter the social media and target profile to extract data:")
        self.instruction_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 20px;")
        self.layout.addWidget(self.instruction_label)

        input_layout = QHBoxLayout()

        # ---------- Social Media Logo (Instagram logo, initially hidden) ----------
        self.logo_instagram = QLabel(self)
        self.logo_instagram.setPixmap(QPixmap("images/logo_instagram.jpg").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_instagram.setVisible(False)  # At the beginning hidden
        input_layout.addWidget(self.logo_instagram)

        # ---------- Social Media dropdown selection ----------
        self.social_media_input = QComboBox(self)
        self.social_media_input.setStyleSheet(Styles.combo_box())
        self.social_media_input.addItems(["Select Social Media", "Instagram"])
        self.social_media_input.setCurrentIndex(0)
        self.social_media_input.currentTextChanged.connect(self.update_logo_social_media)
        input_layout.addWidget(self.social_media_input)

        # ---------- Profile input field ----------
        self.profile_input = QLineEdit(self)
        self.profile_input.setPlaceholderText("Name of the profile")
        self.profile_input.setStyleSheet("padding: 8px; font-size: 14px; background-color: white; border: 2px solid #35308F; border-radius: 6px;")
        input_layout.addWidget(self.profile_input)

        self.layout.addLayout(input_layout)

        # ---------- Start Data Extraction button ----------
        self.extract_button = QPushButton("Start Data Extraction process", self)
        self.extract_button.setStyleSheet(Styles.button_general())
        self.extract_button.clicked.connect(self.extract_data)
        self.layout.addWidget(self.extract_button)

        # ---------- View Dictionary button (initially hidden) ----------
        self.view_dict_button = QPushButton("View Dictionary", self)
        self.view_dict_button.setStyleSheet(Styles.button_general())
        self.view_dict_button.clicked.connect(lambda: self.show_dictionary(self.profile + ".txt"))
        self.view_dict_button.setVisible(False)
        self.layout.addWidget(self.view_dict_button)

        # ---------- Post counters (initially hidden) ----------
        self.counter_label_recientes = QLabel("Recent posts extracted: 0")
        self.counter_label_antiguas = QLabel("Old posts extracted: 0")
        for label in [self.counter_label_recientes, self.counter_label_antiguas]:
            label.setVisible(False)
            label.setStyleSheet("font-weight: bold; font-size: 15px; font-style: italic; margin-top: 20px;")
            self.layout.addWidget(label)

        # ---------- Loading animation and text (initially hidden) ----------
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_pixmap = QPixmap("images/reloj.png").scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.loading_label.setPixmap(self.loading_pixmap)
        self.loading_label.setVisible(False)
        self.layout.addWidget(self.loading_label)

        self.loading_text = QLabel("Accessing the target profile...", self)
        self.loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_text.setStyleSheet("font-size: 14px; font-style: italic;")
        self.loading_text.setVisible(False)
        self.layout.addWidget(self.loading_text)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 15px; font-style: italic; margin-top: 20px;")
        self.layout.addWidget(self.status_label)


    def extract_data(self):
        '''Starts the extraction process after verifying user input and permission'''
        self.page = self.browser.new_page()

        self.crawler = DataExtractor(self.page)

        self.social_media = self.social_media_input.currentText()
        self.profile = self.profile_input.text().strip()

        # Check if user selected social media and entered profile name
        if self.social_media == "Select Social Media":
            self.status_label.setText("⚠️ Please select the social media. ⚠️")
            self.page.close()
            return
        if not self.profile:
            self.status_label.setText("⚠️ Please complete the target profile field. ⚠️")
            self.page.close()
            return
        
        # Show permission dialog before extraction begins
        permission = PermisoDialog(self)
        if permission.exec() != QDialog.DialogCode.Accepted:
            self.status_label.setText("⚠️ Extraction cancelled: permission not granted. ⚠️")
            self.page.close()
            return

        # Check if dictionary already exists for this profile
        diccionario_path = os.path.join("dictionaries", f"{self.profile}.txt")
        if os.path.exists(diccionario_path):
            mensaje = QMessageBox(self)
            mensaje.setWindowTitle("The dictionary already exists")
            mensaje.setText(f"Profile data has already been extracted for '{self.profile}'. Do you want to extract them again?")
            mensaje.setIcon(QMessageBox.Icon.Question)

            # Add buttons
            boton_si = mensaje.addButton("Yes", QMessageBox.ButtonRole.YesRole)
            boton_no = mensaje.addButton("No", QMessageBox.ButtonRole.NoRole)

            mensaje.exec()

            if mensaje.clickedButton() == boton_no:
                self.profile_input.clear()
                self.page.close()
                return

        # Show animation
        self.loading_text.setVisible(True)
        self.loading_label.setVisible(True)

        # Continue with the extraction
        QTimer.singleShot(100, self.continue_execution)

    def continue_execution(self):
        '''Continues the extraction process after permission granted and validation passed'''
        self.output = [self.profile]

        # Start Crawler and extract profile name, bio and total posts
        self.profile_url, self.total_posts, self.info_name_bio = self.crawler.start_crawler("Instagram", self.profile)
        self.output.extend(word for word in self.info_name_bio if word not in self.output)

        self.loading_text.setVisible(False)
        self.loading_label.setVisible(False)

        # Save initial dictionary (contains data from the profile name and bio)
        self.save_dictionary()
        self.status_label.setText(f"Profile name and biography saved in <b>{self.profile}.txt</b>.")

        # Remove initial UI elements
        self.logo_instagram.deleteLater()
        self.instruction_label.deleteLater()
        self.social_media_input.deleteLater()
        self.profile_input.deleteLater()
        self.extract_button.deleteLater()

        # Make the name of the target profile visual in the screen
        self.profile_label = QLabel(f"<b>{self.profile}</b><br>📸 {self.total_posts} posts")
        self.profile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.insertWidget(1, self.profile_label)

        # Set counters to visible
        self.view_dict_button.setVisible(True)
        self.counter_label_recientes.setVisible(True)
        self.counter_label_antiguas.setVisible(True)
        self.counter_label_recientes.setText(f"📥 Recent posts extracted: {self.counter_recents}")
        self.counter_label_antiguas.setText(f"📦 Old posts extracted: {self.counter_old}")

        # If profile has posts → ask how many to extract, else show message
        if self.total_posts != 0:
            self.ask_posts()
        else:
            self.status_label.setText("This profile has no publications so no further information can be extracted.")

    def update_counter_label(self):
        '''To update the counters in the screen'''
        self.counter_label_recientes.setText(f"Recent posts extracted: {self.counter_recents}")
        self.counter_label_antiguas.setText(f"Old posts extracted: {self.counter_old}")

    def ask_posts(self):
        """Request how many posts to extract or to skip them."""
        # Delete previous buttons if they exist
        if hasattr(self, "yes_button"):
            self.yes_button.deleteLater()
            self.no_button.deleteLater()
        
        type = "recent" if self.recent else "old"
        # Here is the logic for controlling overloading when extracting old posts
        if self.recent == False and self.activate_avoid_overloading == False:
            if (self.total_posts - self.counter_recents) > 108:
                self.activate_avoid_overloading = True
                self.status_label.setText(f"The profile's number of posts is too high.\nOlder posts will now be taken " 
                    "from the next 108 posts.\nSelect how many old posts you want to extract or select skip: ")
            else:
                self.status_label.setText(f"Select how many {type} posts you want to extract or select skip:")
        else:
            self.status_label.setText(f"Select how many {type} posts you want to extract or select skip:")

        # Drop-down menu to extract from 1 to 12 posts
        self.n_posts_input = QComboBox(self)
        self.n_posts_input.addItems([str(i) for i in range(1, 13)])
        self.layout.addWidget(self.n_posts_input)

        # Confirm button
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setStyleSheet(Styles.button_general())
        self.confirm_button.clicked.connect(lambda: self.confirm_extraction())
        self.layout.addWidget(self.confirm_button)

        # Skip button
        self.skip_button = QPushButton(f"Do not extract {type} posts", self)
        self.skip_button.setStyleSheet(Styles.button_general())
        self.skip_button.clicked.connect(lambda: self.change_to_old() if self.recent else self.finish_extraction())
        self.layout.addWidget(self.skip_button)
    
    def confirm_extraction(self):
        """To check if it is possible to extract the number of posts the user has selected and then process the posts."""
        try:
            input_publicaciones = int(self.n_posts_input.currentText())

            if self.counter_old + self.counter_recents + input_publicaciones > self.total_posts:
                calculo = self.total_posts - (self.counter_old + self.counter_recents)
                self.status_label.setText(f"There are less posts available. Please select a number ≤ {calculo}")
                return

        except ValueError:
            self.status_label.setText("Please select a valid number.")
            return

        self.status_label.setText(f"Extracting {input_publicaciones} posts...")

        self.n_posts_input.deleteLater()
        self.confirm_button.deleteLater()
        if hasattr(self, "skip_button"):
            self.skip_button.deleteLater()

        posts, counter_scrolls_updated = self.crawler.extract_posts(
            self.recent,
            self.activate_avoid_overloading,
            self.total_posts,
            input_publicaciones,
            self.counter_recents if self.recent else self.counter_old,
            self.counter_recents, # This parameter is necessary to check the overloading condition when extracting the old posts
            self.counter_scroll
        )
        self.counter_scroll = counter_scrolls_updated

        if self.recent:
            self.counter_recents += input_publicaciones
        else:
            self.counter_old += input_publicaciones

        self.update_counter_label()

        filtered_words = self.crawler.filter_words(posts)
        self.output.extend(palabra for palabra in filtered_words if palabra not in self.output)
        self.save_dictionary()

        if (self.counter_old + self.counter_recents) == self.total_posts:
            self.status_label.setText("All posts have been obtained.")
            self.finish_extraction()
        else:
            self.ask_more_posts()

    
    def ask_more_posts(self):
        """Ask if the user wants to extract more posts, deleting previous messages."""
        tipo = "recent" if self.recent else "old"
        self.status_label.setText(f"¿Do you want to extract more {tipo} posts?")
        
        self.yes_button = QPushButton("Yes", self)
        self.yes_button.setStyleSheet(Styles.button_general())
        self.no_button = QPushButton("No", self)
        self.no_button.setStyleSheet(Styles.button_general())

        self.yes_button.clicked.connect(lambda: self.ask_posts())
        self.no_button.clicked.connect(lambda: self.change_to_old() if self.recent else self.finish_extraction())

        self.layout.addWidget(self.yes_button)
        self.layout.addWidget(self.no_button)
    
    def change_to_old(self):
        """Switch from recent to old by deleting previous messages."""
        self.recent = False

        if hasattr(self, "yes_button"):
            self.yes_button.deleteLater()
            self.no_button.deleteLater()
        elif hasattr(self, "skip_button"):
            self.skip_button.deleteLater()
            self.confirm_button.deleteLater()
            self.n_posts_input.deleteLater()

        self.ask_posts()

    def finish_extraction(self):
        """Finishes the extraction and cleans the interface."""
        if hasattr(self, "yes_button"):
            try:
                self.yes_button.deleteLater()
                self.no_button.deleteLater()
            except RuntimeError:
                pass  
        
        if hasattr(self, "skip_button"):
            try:
                self.skip_button.deleteLater()
                self.confirm_button.deleteLater()
                self.n_posts_input.deleteLater()
            except RuntimeError:
                pass  
        
        self.status_label.setText("Extraction completed. Saving results...")
        self.save_dictionary()
        self.browser.close()

        # Reset all variables for the next time data is extracted for a new profile
        self.counter_recents = 0  
        self.counter_old = 0   
        self.output = [] 
        self.recent = True 
        self.activate_avoid_overloading = False
        self.counter_scroll = 0 


    def save_dictionary(self):
        """Save the dictionary to a text file."""
        try:
            with open("dictionaries/" + self.profile + ".txt", "w", encoding="utf-8") as file:
                file.write("\n".join(self.output))
        except Exception as e:
            self.status_label.setText(f"Error saving file: {e}")

    def show_dictionary(self, file):
        """Opens a new window to display the profile dictionary."""
        self.descripcion_window = WindowDictionary(file)
        self.descripcion_window.show()
    
    def return_main_menu(self):
        """Close Playwright before returning to the main menu"""
        if hasattr(self, 'p') and self.p is not None:
            self.p.stop()  # Stops Playwright if it is running
            self.p = None  # Resets the variable to avoid future problems
        self.back_button.deleteLater()
        self.init_ui() 
    
    def update_logo_social_media(self, text):
        '''To insert in the screen the logo of the social media selected'''
        if text == "Instagram":
            self.logo_instagram.setVisible(True)
        else:
            self.logo_instagram.setVisible(False)

    def closeEvent(self,event):
        """Closes Playwright and the browser when closing the app."""
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUIModule()
    window.show()
    sys.exit(app.exec())