import subprocess
import threading
import re
from types import NoneType
import gi


from gi.repository import Adw, GLib, Gtk
from gi.repository.GObject import idle_add


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
        # self.entry_row = Adw.EntryRow()
        # self.entry_row.set_title("Enter Video Name")

        # combo row
        self.combo_row = Adw.ComboRow()
        self.combo_row.set_title("Codecs")
        self.combo_row.set_model(Gtk.StringList.new(["H.264", "HEVC", "Av1"]))

        # switch row
        self.switch_row = Adw.SwitchRow(title="Hardware Acceleration")

        # add widgets to the preferences group
        # self.group.add(self.entry_row)
        self.group.add(self.combo_row)
        self.group.add(self.switch_row)
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
            action=Gtk.FileChooserAction.SAVE,
        )
        file_dialog.set_size_request(800, 600)

        file_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        file_dialog.add_button("Save", Gtk.ResponseType.ACCEPT).add_css_class(
            "suggested-action"
        )

        file_dialog.connect("response", self.file_dialog_responce)
        file_dialog.present()
        self.converting_button.set_sensitive(False)

    def file_dialog_responce(self, dialog, responce):
        if responce == Gtk.ResponseType.ACCEPT:
            video_path = self.main_page.video_path
            folder = dialog.get_file().get_path()
            codec = self.get_selected_codec("")
            dialog.destroy()

            self.progress_win = Progress_window(self.main_window)
            self.progress_win.present()
            thread = threading.Thread(
                target=self.run_the_converter,
                args=(video_path, folder, codec),
            )
            thread.start()

        dialog.destroy()
        self.converting_button.set_sensitive(True)

    def run_the_converter(self, video_path, folder, codec):
        ffmpeg = Ffmpeg()
        ffmpeg.get_video_path(video_path)
        if codec == "H.264":
            codec = "libx264"
            if self.switch_row.get_active():
                codec = "h264_nvenc"
            ffmpeg.convert_video(
                self,
                codec,
                folder,
            )
        elif codec == "HEVC":
            codec = "libx265"
            if self.switch_row.get_active():
                codec = "hevc_nvenc"
            ffmpeg.convert_video(
                self,
                codec,
                folder,
            )
        else:
            codec = "libsvtav1"
            if self.switch_row.get_active():
                codec = "av1_nvenc"
            ffmpeg.convert_video(
                self,
                codec,
                folder,
            )


class Progress_window(Adw.Window):
    def __init__(self, parent):
        super().__init__()
        self.cancellation = False
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Conversion Progress")
        self.set_default_size(400, 200)

        # main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.set_content(self.main_box)

        # center box
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.center_box.set_hexpand(True)
        self.center_box.set_vexpand(True)
        self.main_box.append(self.center_box)

        # clamp
        self.clamp = Adw.Clamp()
        self.center_box.append(self.clamp)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.clamp.set_child(self.clamp_box)

        # status label
        self.status_label = Gtk.Label(label="Converting The Video")
        self.status_label.add_css_class("title-3")
        self.clamp_box.append(self.status_label)

        # progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0)
        self.progress_bar.set_margin_start(15)
        self.progress_bar.set_margin_end(15)
        self.clamp_box.append(self.progress_bar)

        # cancel button
        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.add_css_class("destructive-action")
        self.cancel_button.connect("clicked", self.cancel_state)
        self.cancel_button_clamp = Adw.Clamp()
        self.center_box.append(self.cancel_button_clamp)
        self.cancel_button_clamp.set_maximum_size(50)
        self.cancel_button_clamp.set_child(self.cancel_button)

    def update_progress_bar(self, progress):
        self.progress_bar.set_fraction(progress)

    def process_end(self):
        self.hide()
        self.destroy()

    def cancel_state(self, _):
        self.cancellation = True


class Ffmpeg:
    def __ini__(self):
        self.video_path = None
        self.duration = None

    def convert_video(self, window, codec, output_path):
        process = subprocess.Popen(
            f"ffmpeg -y -i {self.video_path} -c:v {codec} -c:a copy {output_path}",
            shell=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in process.stderr:
            if self.cancel_process(process, window.progress_win, output_path) == "done":
                break
            same = re.search(r"time=(\d+):(\d+):(\d+.\d+)", line)
            if same is not None:
                hours, minutes, seconds = map(float, same.groups())
                progress = (
                    self.convert_time_to_seconds(hours, minutes, seconds)
                    / self.get_video_duration()
                )
                print(progress)
                GLib.idle_add(window.progress_win.update_progress_bar, progress)

        GLib.idle_add(window.progress_win.process_end)

    def get_video_duration(self):
        duration = subprocess.run(
            f"ffprobe -i {self.video_path} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1",
            capture_output=True,
            shell=True,
        )
        return float(duration.stdout)

    def get_video_path(self, video_path):
        self.video_path = video_path

    def convert_time_to_seconds(self, hours, minutes, seconds):
        hours = hours * 60 * 60
        minutes *= 60
        return seconds + minutes + hours

    def cancel_process(self, process, progress_win, output_video_path):
        if progress_win.cancellation:
            GLib.idle_add(progress_win.process_end)
            process.kill()
            subprocess.run(f"rm {output_video_path}", shell=True)
            return "done"
