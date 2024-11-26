import gi
gi.require_version("Gtk","4.0")
from gi.repository import Gtk

class App_name_label(Gtk.Label):
    def __init__(self,*args):
        super().__init__(*args, label="Green Film")
        self.add_css_class("title-1")
        self.set_margin_bottom(5)
