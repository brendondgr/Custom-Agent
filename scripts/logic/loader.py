import os

from scripts.logic.icons import IconLoader
from scripts.logic.audio import AudioDevices, AudioRouting
from scripts.qt.labels import LabelPrefs

class Loader:
    def __init__(self, dir, audio_values):
        # Audio Values
        self.audio_values = audio_values
        
        # Directories
        self.icons_dir = os.path.join(dir, 'icons')
        self.json_dir = os.path.join(dir, 'json')
        
        # Print that gives Information for the loaded libraries
        self.print_library_info()
        
        # Individual Libraries
        self.icons = IconLoader(self.icons_dir)
        self.audio_devices = AudioDevices()
        self.audio_routing = AudioRouting(self.audio_devices, self.audio_values)
        self.labels = LabelPrefs()
        
    def print_library_info(self):
        print(f"Icons Directory: {self.icons_dir}")
        print(f"JSON Directory: {self.json_dir}")