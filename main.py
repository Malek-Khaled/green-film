import gi
import threading
import second_page
from main_page import Main_page

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_page = Main_page(self)
        self.set_size_request(600, 480)
        self.set_default_size(1280, 720)

        # navigation view
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)
        main_P = self.main_page.get_the_page()
        self.navigation_view.push(main_P)


class Myapp(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = Myapp()
app.run(None)
