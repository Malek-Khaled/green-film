import gi
gi.require_version("Gtk","4.0")
from gi.repository import Gtk

class App_logo(Gtk.Image):
    def __init__(self, path, *args):
        super().__init__(*args)
        self.logo_path = path + "/greenfilm-logo.svg"
        self.set_from_file(self.logo_path)
        self.set_pixel_size(150)
        self.set_margin_bottom(25)
        self.add_css_class("icon-dropshadow")
