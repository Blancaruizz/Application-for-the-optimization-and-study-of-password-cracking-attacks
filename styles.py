class Styles:
    '''Here all the neccessary styles for buttons and menus are defined to reduce code in main.py'''
    @staticmethod
    def button_general():
        return """
            QPushButton {
                font-size: 14px;
                padding: 6px 12px;
                background-color: #35308F;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4B44B4;
            }
        """

    @staticmethod
    def combo_box():
        return """
            QComboBox {
                padding: 8px;
                font-size: 14px;
                background-color: white;
                border: 2px solid #35308F;
                border-radius: 6px;
            }
        """
    
    @staticmethod
    def expand_gemini():
        return """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
    
    @staticmethod
    def reduce_gemini():
        return """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #dc3545;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """
    
    @staticmethod
    def simple_mode():
        return """
            QPushButton {
                background-color: #5bc0de;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #31b0d5;
            }
        """
    
    @staticmethod
    def intermediate_mode():
        return """
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """
    
    @staticmethod
    def advanced_mode():
        return """
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """
    
    @staticmethod
    def text_edit():
        return """
            QTextEdit {
                background-color: #f8f8f8;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                padding: 10px;
            }
        """