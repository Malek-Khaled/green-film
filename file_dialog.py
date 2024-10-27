import gi
from gi.repository import Gtk


class File_dialog(Gtk.FileDialog):
    def __init__(self, *args, title):
        super().__init__(*args, title=title)
        self.set_modal(True)

    @staticmethod
    def file_dialog_save(_, parent, callback):
        file_dialog = File_dialog(title="Output Folder")
        file_dialog.save(parent, None, callback)
