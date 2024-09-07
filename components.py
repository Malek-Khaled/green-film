import subprocess, gi, os

gi.require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GLib, Gdk

absolute_path = os.path.dirname(__file__)


class Main_page:
    def __init__(self, main_window):
        self.main_window = main_window
        self.first_page = Adw.NavigationPage()
        self.first_page.set_title("select file")

        # main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)

        # center box
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.center_box.set_hexpand(True)
        self.center_box.set_vexpand(True)

        # header bar
        self.headerbar = Adw.HeaderBar()
        self.window_title = Adw.WindowTitle(title="Green Film")
        self.headerbar.set_title_widget(self.window_title)
        self.main_box.append(self.headerbar)

        # clamp
        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(400)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # add
        self.main_box.append(self.center_box)
        self.clamp.set_child(self.clamp_box)
        self.center_box.append(self.clamp)

        # Logo
        self.logo_clamp = Adw.Clamp()
        self.logo_clamp.set_maximum_size(170)
        self.app_logo = Gtk.Picture()
        self.logo_path = absolute_path + "/greenfilm-logo.svg"
        self.app_logo.set_margin_bottom(25)
        self.set_logo(self.logo_path, 1200)
        self.logo_clamp.set_child(self.app_logo)
        self.clamp_box.append(self.logo_clamp)

        # input group
        self.group = Adw.PreferencesGroup()
        # button
        self.button = Gtk.Button(label="Add a Video")
        self.button.add_css_class("suggested-action")
        self.button.add_css_class("pill")
        self.button.set_margin_top(25)
        self.button.connect("clicked", self.file_dialog_open)
        # combo row
        self.combo_row = Adw.ComboRow()
        self.combo_row.set_title("Codecs")
        self.combo_row.set_model(Gtk.StringList.new(["H.264", "HEVC", "Av1"]))

        # app name label
        self.app_name_label = Gtk.Label(label="Green Film")
        self.app_name_label.add_css_class("large-title")
        self.app_name_label.add_css_class("title-1")
        self.app_name_label.set_margin_bottom(5)

        # app description label
        self.description_label = Gtk.Label(label="Add A Video To Start Converting")

        # add widgets to preferences group
        # self.group.add(self.combo_row)
        self.group.add(self.app_name_label)
        self.group.add(self.description_label)
        self.group.add(self.button)
        self.clamp_box.append(self.group)

        self.first_page.set_child(self.main_box)

    def get_selected_codec(self, _):
        selected_codec_index = self.combo_row.get_selected()
        return self.combo_row.get_model().get_string(selected_codec_index)

    def file_dialog_open(self, _):
        file_dialog = Gtk.FileChooserDialog(
            title="Choose a video",
            parent=MainWindow(),
            action=Gtk.FileChooserAction.OPEN,
        )
        file_dialog.set_size_request(800, 600)

        file_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        file_dialog.add_button("Open", Gtk.ResponseType.ACCEPT).add_css_class(
            "suggested-action"
        )
        file_dialog.connect("response", self.file_dialog_responce)
        file_dialog.present()

    def file_dialog_responce(self, dialog, responce):
        if responce == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            dialog.destroy()
            second_page = Second_page(self).get_page()
            self.main_window.navigation_view.push(second_page)
            return file_path

        dialog.destroy()

    def load_svg(self, path, size):
        file = Gio.File.new_for_path(path)
        stream = file.read()
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(
            stream, size, size, True, None
        )
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        return texture

    def set_logo(self, logo_path, size):
        logo_texture = self.load_svg(self.logo_path, size)
        self.app_logo.set_paintable(logo_texture)

    def get_the_page(self):
        return self.first_page


class Second_page:
    def __init__(self, main_page):
        self.main_page = main_page
        self.second_page = Adw.NavigationPage()
        self.second_page.set_title("select file")
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.headerbar = Adw.HeaderBar()
        self.main_box.append(self.headerbar)
        self.second_page.set_child(self.main_box)

    def get_page(self):
        return self.second_page


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        main_page = Main_page(self)
        super().__init__(*args, **kwargs)
        self.set_size_request(600, 480)
        self.set_default_size(1280, 720)

        # navigation view
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)
        main_page = main_page.get_the_page()
        self.navigation_view.push(main_page)


class Myapp(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = Myapp()
app.run(None)
