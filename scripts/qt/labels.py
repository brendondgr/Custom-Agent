from PySide6.QtGui import QFont
from PySide6.QtGui import QColor

class LabelPrefs:
    @staticmethod
    def Font(font_name, size, color=None):
        font = QFont(font_name, size)
        if color is not None:
            font.setColor(QColor(color))
        return font
    
    @staticmethod
    def Font_b(font_name, size, color=None):
        font = QFont(font_name, size)
        font.setBold(True)
        if color is not None:
            font.setColor(QColor(color))
        return font
    
    @staticmethod
    def Font_bu(font_name, size, color=None):
        font = QFont(font_name, size)
        font.setBold(True)
        font.setUnderline(True)
        if color is not None:
            font.setColor(QColor(color))
        return font
    
    @staticmethod
    def Font_u(font_name, size, color=None):
        font = QFont(font_name, size)
        font.setUnderline(True)
        if color is not None:
            font.setColor(QColor(color))
        return font
