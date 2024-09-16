import subprocess
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk


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


class Ffmpeg:
    def convert_video(self, video_path, codec, output_name):
        subprocess.run(
            f"ffmpeg -i {video_path} -c:v {codec} {output_name}",
            shell=True,
            stdout=subprocess.PIPE,
        )
