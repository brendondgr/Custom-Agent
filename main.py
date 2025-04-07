from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTableWidget, QPushButton,
    QTabWidget, QFormLayout, QComboBox, QCheckBox, 
    QRadioButton, QSlider, QSpinBox, QDoubleSpinBox,
    QDateEdit, QDateTimeEdit, QTimeEdit, QDial,
    QProgressBar, QScrollBar, QSlider, QLCDNumber,
    QSplitter, QStackedWidget, QToolBox, QToolButton,
    QGroupBox, QScrollArea, QDockWidget, QMenuBar,
    QStatusBar, QToolBar, QStatusBar, QDockWidget,
    QMainWindow, QMenu, QDialog, QFileDialog,
)
from PySide6.QtCore import Qt

import sys
import os

from scripts.logic.loader import Loader
from scripts.logic.audio import AudioValues
from scripts.qt.audio_module import AudioSelectionWidget, AudioManipulation
# from scripts.qt.menu_bar import MenuBar

class MainApp(QMainWindow):
    def __init__(self):
        # Clear Console.
        if sys.platform == 'win32': os.system('cls')
        else: os.system('clear')
        
        print("\033[94m-- Directories --\033[0m")
        # Get Working Directory of This File.
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        print(f'The current working directory is: {self.working_dir}')
        
        # Create Audio Volumes Instance
        self.audio_values = AudioValues()
        
        # Load the Scripts for the Loader
        self.loader = Loader(self.working_dir, self.audio_values)
        
        super().__init__()
        self.setWindowTitle("Custom Soundboard Application")
        self.setGeometry(100, 100, 500, 300)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop)
        
        # Create a QVBoxLayout
        audio_layout = QVBoxLayout()
        
        # Create an audio selection widget
        self.audio_widget = AudioSelectionWidget(self.loader)
        audio_layout.addWidget(self.audio_widget, alignment=Qt.AlignTop)
        
        # Create an audio manipulation widget
        self.audio_manipulation = AudioManipulation(self.loader)
        audio_layout.addWidget(self.audio_manipulation, alignment=Qt.AlignTop)
        
        # Add the audio layout to the main layout
        layout.addLayout(audio_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainApp()
    gui.show()
    sys.exit(app.exec())