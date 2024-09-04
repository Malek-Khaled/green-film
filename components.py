import subprocess, gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_size_request(600, 480)
        self.set_default_size(1280, 720)

        # main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.set_content(self.main_box)

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

        self.app_logo = Gtk.Image()
        self.app_logo.set_from_file(
            "/home/malek/Pictures/ffmpeg-converter-gnome-logo.svg"
        )
        self.app_logo.set_pixel_size(150)
        self.app_logo.set_margin_bottom(25)

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
        self.description_label = Gtk.Label(
            label="Add a Video To Start Codec Converting"
        )

        # add widgets to preferences group
        # self.group.add(self.combo_row)
        self.group.add(self.app_logo)
        self.group.add(self.app_name_label)
        self.group.add(self.description_label)
        self.group.add(self.button)
        self.clamp_box.append(self.group)

    def get_selected_codec(self, _):
        selected_codec_index = self.combo_row.get_selected()
        return self.combo_row.get_model().get_string(selected_codec_index)

    def file_dialog_open(self, _):
        file_dialog = Gtk.FileChooserDialog(
            title="Choose a video", parent=self, action=Gtk.FileChooserAction.OPEN
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
            return file_path

        dialog.destroy()


class Myapp(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = Myapp()

app.run(None)


class Video:
    def __init__(self):
        self.location = ""
        self.name = ""

    def find_video_location(self):
        output = subprocess.run(
            ['zenity --file-selection --title="Select a Video"'],
            shell=True,
            capture_output=True,
        )

        location_with_appendages = str(output).split(",")[2]
        location = location_with_appendages[10:-3]

        self.find_video_name(location.split("/")[-1])
        self.location = location

    def find_video_name(self, name):
        self.name = name


class Ffmpeg:
    def __init__(self):
        self.video = Video()

    def export_ffmpeg_output_file(self):
        output = subprocess.run(
            ['zenity --file-selection --directory --save --title="Select a File"'],
            shell=True,
            capture_output=True,
        )

        location_with_appendages = str(output).split(",")[2]
        location = location_with_appendages[10:-3]

        return location

    def video_converter(self):
        self.video.find_video_location()
        output_path = self.export_ffmpeg_output_file()
        codec = input("enter video codec: ")
        output_file_name = input("enter output file name: ")
        subprocess.run(
            f"ffmpeg -i {self.video.location} -c:v {codec} -crf 24 {output_path}/{output_file_name}",
            shell=True,
        )
