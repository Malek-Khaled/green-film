import os
import subprocess
import gi
import threading

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk

absolute_path = os.path.dirname(__file__)


class Main_page:
    def __init__(self, main_window):
        self.main_window = main_window
        self.first_page = Adw.NavigationPage()
        self.first_page.set_title("Green Film")
        self.video_path = ""
        self.video_name = ""

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
        self.main_box.append(self.headerbar)
        self.headerbar.add_css_class("flat")

        # clamp
        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(400)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # add
        self.main_box.append(self.center_box)
        self.clamp.set_child(self.clamp_box)
        self.center_box.append(self.clamp)

        # Logo
        self.logo_path = absolute_path + "/greenfilm-logo.svg"
        self.app_logo = Gtk.Image()
        self.app_logo.set_from_file(self.logo_path)
        self.app_logo.set_pixel_size(150)
        self.app_logo.set_margin_bottom(25)
        self.app_logo.add_css_class("icon-dropshadow")
        self.clamp_box.append(self.app_logo)

        # input group
        self.group = Adw.PreferencesGroup()
        # button
        self.button = Gtk.Button(label="Add a Video")
        self.button.add_css_class("suggested-action")
        self.button.add_css_class("pill")
        self.button.set_margin_top(25)
        self.button.connect("clicked", self.file_dialog_open)

        # app name label
        self.app_name_label = Gtk.Label(label="Green Film")
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

    def file_dialog_open(self, _):
        file_dialog = Gtk.FileChooserDialog(
            title="Choose a video",
            parent=self.main_window,
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
            file_name = dialog.get_file().get_basename()
            self.video_path = file_path
            self.video_name = file_name
            dialog.destroy()
            second_page = Second_page(self, self.main_window).get_page()
            self.main_window.navigation_view.push(second_page)

        dialog.destroy()

    def get_the_page(self):
        return self.first_page


class Second_page:
    def __init__(self, main_page, main_window):
        self.main_page = main_page
        self.main_window = main_window
        self.second_page = Adw.NavigationPage()
        self.second_page.set_title(main_page.video_name)

        # main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.second_page.set_child(self.main_box)

        # headerbar
        self.headerbar = Adw.HeaderBar()
        self.headerbar.add_css_class("flat")

        self.main_box.append(self.headerbar)

        # center box
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.center_box.set_hexpand(True)
        self.center_box.set_vexpand(True)
        self.main_box.append(self.center_box)

        # clamp and clamp box
        self.clamp = Adw.Clamp()
        self.center_box.append(self.clamp)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.clamp.set_child(self.clamp_box)

        # preferences group
        self.group = Adw.PreferencesGroup()

        # entry row
        self.entry_row = Adw.EntryRow()
        self.entry_row.set_title("Enter Video Name")

        # combo row
        self.combo_row = Adw.ComboRow()
        self.combo_row.set_title("Codecs")
        self.combo_row.set_model(Gtk.StringList.new(["H.264", "HEVC", "Av1"]))

        # add widgets to the preferences group
        self.group.add(self.entry_row)
        self.group.add(self.combo_row)
        self.clamp_box.append(self.group)

        # converting button
        self.converting_button = Gtk.Button(label="Convert")
        self.clamp_box.append(self.converting_button)
        self.converting_button.add_css_class("suggested-action")
        self.converting_button.add_css_class("pill")
        self.converting_button.set_margin_top(15)
        self.converting_button.connect("clicked", self.file_dialog_save)

    def get_selected_codec(self, _=""):
        selected_codec_index = self.combo_row.get_selected()
        return self.combo_row.get_model().get_string(selected_codec_index)

    def get_page(self):
        return self.second_page

    def color_change(self, button):
        button.add_css_class("suggested-action")
        button.remove_css_class("dim-label")

    def file_dialog_save(self, _=""):
        file_dialog = Gtk.FileChooserDialog(
            title="choose a folder",
            parent=self.main_window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        file_dialog.set_size_request(800, 600)

        file_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        file_dialog.add_button("Save", Gtk.ResponseType.ACCEPT).add_css_class(
            "suggested-action"
        )
        file_dialog.connect("response", self.file_dialog_responce)
        file_dialog.present()

    def file_dialog_responce(self, dialog, responce):
        if responce == Gtk.ResponseType.ACCEPT:
            video_path = self.main_page.video_path
            folder = dialog.get_file().get_path()
            output_video_name = self.entry_row.get_text()
            codec = self.get_selected_codec("")
            dialog.destroy()

            thread = threading.Thread(
                target=self.run_the_converter,
                args=(video_path, folder, output_video_name, codec),
            )
            thread.start()

    def run_the_converter(self, video_path, folder, output_name, codec):
        ffmpeg = Ffmpeg()
        if codec == "H.264":
            ffmpeg.convert_video(
                video_path,
                "libx264",
                f"{folder}/{output_name}.mp4",
            )
        elif codec == "HEVC":
            ffmpeg.convert_video(
                video_path,
                "libx265",
                f"{folder}/{output_name}.mp4",
            )
        else:
            ffmpeg.convert_video(
                video_path,
                "libsvtav1",
                f"{folder}/{output_name}.mp4",
            )


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_page = Main_page(self)
        self.set_size_request(600, 480)
        self.set_default_size(1280, 720)

        # navigation view
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)
        main_page = self.main_page.get_the_page()
        self.navigation_view.push(main_page)


class Myapp(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


class Ffmpeg:
    def convert_video(self, video_path, codec, output_name):
        subprocess.run(
            f"ffmpeg -i {video_path} -c:v {codec} {output_name}",
            shell=True,
            stdout=subprocess.PIPE,
        )


app = Myapp()
app.run(None)
