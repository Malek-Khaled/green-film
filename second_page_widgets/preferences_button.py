import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

class Preferences_button:
    def __init__(self, box, show_preferences_dialog_function):
        self.preferences_button = Gtk.Button(icon_name="open-menu-symbolic")
        self.preferences_button.set_valign(Gtk.Align.CENTER)
        self.preferences_button.set_margin_top(15)
        self.preferences_button.connect("clicked", show_preferences_dialog_function)
        box.append(self.preferences_button)
