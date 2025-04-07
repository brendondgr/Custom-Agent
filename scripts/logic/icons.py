import os

class IconLoader:
    def __init__(self, icons_dir):
        self.icons_dir = icons_dir
        self.icons = {}
        self.load_icons()

    def load_icons(self):
        for filename in os.listdir(self.icons_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                name, ext = os.path.splitext(filename)
                self.icons[name] = os.path.join(self.icons_dir, filename)

    def get_icon(self, name):
        return self.icons.get(name)

    def list_icons(self):
        return list(self.icons.keys())

    def add_icon(self, name, file_path):
        if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
            self.icons[name] = file_path
        else:
            raise ValueError("Invalid file path or unsupported file type")
