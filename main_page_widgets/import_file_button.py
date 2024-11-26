import gi
from file_dialog import File_dialog
gi.require_version("Gtk","4.0")
from gi.repository import Gtk

class Import_file_button(Gtk.Button):
    def __init__(self, main_window, file_dialog_result_function,*args):
        super().__init__(*args, label="Add A Video")
        self.add_css_class("suggested-action")
        self.add_css_class("pill")
        self.set_margin_top(25)
        self.connect(
            "clicked",
            File_dialog.file_dialog_open,
            main_window,
            file_dialog_result_function
        )
