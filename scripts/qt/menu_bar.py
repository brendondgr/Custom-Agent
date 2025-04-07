from PySide6.QtWidgets import QMenuBar

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)  # Set fixed height for the entire menu bar
        
        # Values...
        self.height = 45
        self.width = 45
        
        # File button
        file_button = self.addMenu("File")
        file_button.triggered.connect(self.on_file_clicked)
        file_button.setFixedSize(self.width, self.height)

        # Edit button
        edit_button = self.addMenu("Edit")
        edit_button.triggered.connect(self.on_edit_clicked)
        edit_button.setFixedSize(self.width, self.height)

        # Help button
        help_button = self.addMenu("Help")
        help_button.triggered.connect(self.on_help_clicked)
        help_button.setFixedSize(self.width, self.height)

        # Set button styles
        button_style = "QMenuBar::item { padding: 5px 10px; }"
        self.setStyleSheet(button_style)

    def on_file_clicked(self):
        print("File clicked")

    def on_edit_clicked(self):
        print("Edit clicked")

    def on_help_clicked(self):
        print("Help clicked")
