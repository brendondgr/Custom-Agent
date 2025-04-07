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
from PySide6.QtGui import QIcon, QPixmap
from scripts.logic.audio import AudioValues

class AudioSelectionWidget(QWidget):
    def __init__(self, logic, parent=None):
        super().__init__(parent)
        self.icon = logic.icons
        self.labels = logic.labels
        self.audio_routing = logic.audio_routing
        self.audio_devices = logic.audio_devices
        self.output_devices = self.audio_devices.outputs
        self.input_devices = self.audio_devices.inputs
        self.initUI()

    def initUI(self):
        label_width = 100  # Maximum label width
        audio_layout = QVBoxLayout(self)
        audio_layout.setAlignment(Qt.AlignTop)
        
        # Layout
        first_row = QHBoxLayout()
        first_row.setAlignment(Qt.AlignTop)
        audio_layout.addLayout(first_row)
        
        # 'Audio' Label
        audio_label = QLabel("Audio")
        audio_label.setAlignment(Qt.AlignLeft)
        audio_label.setFont(self.labels.Font_bu('Segoe UI', 15))
        audio_label.setFixedWidth(100)
        first_row.addWidget(audio_label)
        
        # Load the "refresh" icon
        refresh_icon = self.icon.get_icon("refresh")
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon(QPixmap(refresh_icon)))
        refresh_button.clicked.connect(self.refresh_devices)
        first_row.addWidget(refresh_button)
        
        # Add the "play" icon
        play_icon = self.icon.get_icon("play")
        start_button = QPushButton(" Start")
        start_button.setIcon(QIcon(QPixmap(play_icon)))
        start_button.clicked.connect(self.start_route)
        first_row.addWidget(start_button)
        
        # Add the "stop" icon
        stop_icon = self.icon.get_icon("stop")
        stop_button = QPushButton(" Stop")
        stop_icon_pixmap = QPixmap(stop_icon)
        stop_icon_pixmap = stop_icon_pixmap.scaled(15, 15, Qt.KeepAspectRatio)
        stop_button.setIcon(QIcon(stop_icon_pixmap))
        stop_button.clicked.connect(self.stop_route)
        first_row.addWidget(stop_button)
        
        # Audio Output
        output_layout = QHBoxLayout()
        output_layout.setAlignment(Qt.AlignTop)
        output_layout.addWidget(self.createLabel("Audio Output:", label_width))
        output_dropdown = QComboBox()
        output_dropdown.addItems(self.output_devices.keys())
        output_layout.addWidget(output_dropdown)
        audio_layout.addLayout(output_layout)

        # Mic Input
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignTop)
        input_layout.addWidget(self.createLabel("Mic Input:", label_width))
        input_dropdown = QComboBox()
        input_dropdown.addItems(self.input_devices.keys())
        input_layout.addWidget(input_dropdown)
        audio_layout.addLayout(input_layout)

        # Mic Output
        mic_output_layout = QHBoxLayout()
        mic_output_layout.setAlignment(Qt.AlignTop)
        mic_output_layout.addWidget(self.createLabel("Mic Output:", label_width))
        mic_output_dropdown = QComboBox()
        mic_output_dropdown.addItems(self.output_devices.keys())
        if len(self.output_devices) > 1:
            mic_output_dropdown.setCurrentIndex(1)
        mic_output_layout.addWidget(mic_output_dropdown)
        audio_layout.addLayout(mic_output_layout)

        self.output_dropdown = output_dropdown
        self.input_dropdown = input_dropdown
        self.mic_output_dropdown = mic_output_dropdown

    def createLabel(self, text, width):
        label = QLabel(text)
        label.setFixedWidth(width)
        return label

    def refresh_devices(self):
        self.audio_devices.refresh_devices()
        self.output_devices = self.audio_devices.outputs
        self.input_devices = self.audio_devices.inputs
        self.output_dropdown.clear()
        self.input_dropdown.clear()
        self.mic_output_dropdown.clear()
        self.output_dropdown.addItems(self.output_devices.keys())
        self.input_dropdown.addItems(self.input_devices.keys())
        self.mic_output_dropdown.addItems(self.output_devices.keys())
        if len(self.output_devices) > 1:
            self.mic_output_dropdown.setCurrentIndex(1)
    
    def start_route(self):
        self.audio_output = self.output_devices[self.output_dropdown.currentText()]
        self.audio_input = self.input_devices[self.input_dropdown.currentText()]
        self.audio_mic_output = self.output_devices[self.mic_output_dropdown.currentText()]
        
        # Start Routing the Audio
        self.audio_routing.start_route(self.audio_output, self.audio_input, self.audio_mic_output)
    
    def stop_route(self):
        self.audio_routing.stop_route()
        

class AudioManipulation(QWidget):
    def __init__(self, logic, parent=None):
        super().__init__(parent)
        self.audio_values = logic.audio_values
        self.icon = logic.icons
        self.labels = logic.labels
        self.audio_routing = logic.audio_routing
        self.audio_devices = logic.audio_devices
        self.output_devices = self.audio_devices.outputs
        self.input_devices = self.audio_devices.inputs
        self.initUI()

    def initUI(self):
        # Establish Layout, QVBoxLayout
        layout = QVBoxLayout()
        self.setLayout(layout)
        label_width = 100
        
        # ###############################
        # ##     First Row - Bools     ##
        # ###############################
        # #### Spectrum ####
        # spectrum_layout = QHBoxLayout()
        # spectrum_layout.setAlignment(Qt.AlignTop)
        # spectrum_checkbox = QCheckBox("Spectrum")
        # spectrum_checkbox.setChecked(self.audio_values.get_spectrum())
        # spectrum_layout.addWidget(spectrum_checkbox)
        # layout.addLayout(spectrum_layout)
        # spectrum_checkbox.stateChanged.connect(self.update_spectrum)
        
        ###############################
        ##      Volume Increaser     ##
        ###############################
        volume_layout = QHBoxLayout()
        volume_layout.setAlignment(Qt.AlignTop)
        volume_layout.addWidget(self.createLabel("Volume:", label_width))
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(10000)
        volume_slider.setSingleStep(100)
        volume_slider.setValue(100)
        volume_layout.addWidget(volume_slider)
        self.volume_label = QLabel("100%")
        self.volume_label.setFixedWidth(40)
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)
        volume_slider.valueChanged.connect(lambda value: self.volume_label.setText(f"{value/100:.0f}%"))
        volume_slider.valueChanged.connect(self.update_volume)
        
        ###############################
        ##      Noise Threshold      ##
        ###############################
        noise_threshold_layout = QHBoxLayout()
        noise_threshold_layout.setAlignment(Qt.AlignTop)
        noise_threshold_layout.addWidget(self.createLabel("Noise Threshold:", label_width))
        noise_threshold_slider = QSlider(Qt.Horizontal)
        noise_threshold_slider.setMinimum(0)
        noise_threshold_slider.setMaximum(50)
        noise_threshold_slider.setSingleStep(1)
        noise_threshold_slider.setValue(0)
        noise_threshold_layout.addWidget(noise_threshold_slider)
        self.noise_threshold_label = QLabel("0.00000")
        self.noise_threshold_label.setFixedWidth(50)
        noise_threshold_layout.addWidget(self.noise_threshold_label)
        layout.addLayout(noise_threshold_layout)
        noise_threshold_slider.valueChanged.connect(self.update_noise_threshold)
    
    def update_noise_threshold(self, value):
        self.audio_values.set_noise_threshold(value/100000)
        self.noise_threshold_label.setText(f"{value/100000:.5f}")
    
    def update_volume(self, value):
        self.audio_values.set_volume(value)
        self.volume_label.setText(f"{value:.0f}%")
        
    def update_spectrum(self, state):
        self.audio_values.set_spectrum(state)
    
    def createLabel(self, text, width):
        label = QLabel(text)
        label.setFixedWidth(width)
        return label