import gi
from file_dialog import File_dialog

gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

class Converting_button:
    def __init__(self, box, main_window, file_dialog_result_function):
        self.converting_button = Gtk.Button(label="Convert")
        self.converting_button.set_sensitive(False)
        self.converting_button.set_hexpand(True)
        box.append(self.converting_button)
        self.converting_button.add_css_class("suggested-action")
        self.converting_button.add_css_class("pill")
        self.converting_button.set_margin_top(15)
        self.converting_button.connect(
            "clicked",
            File_dialog.file_dialog_save,
            main_window,
            file_dialog_result_function
        )
