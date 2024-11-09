import subprocess
import string
import threading
import re
from file_dialog import File_dialog
import gi


from gi.repository import Adw, GLib, Gtk
from gi.repository.GObject import idle_add


class Second_page:
    def __init__(self, main_page, main_window):
        self.main_page = main_page
        self.main_window = main_window
        self.second_page = Adw.NavigationPage()
        self.preferences_dialog = Preferences_dialog(self)
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

        # entry row
        self.entry_box = Gtk.Box(spacing=6)
        self.clamp_box.append(self.entry_box)

        self.entry_field = Adw.EntryRow()
        self.entry_field.set_max_length(30)
        self.entry_field.connect("changed", self.on_entry_changed)
        self.entry_field.set_title("Video Name")
        self.entry_field.set_hexpand(True)

        self.entry_group = Adw.PreferencesGroup()
        self.entry_box.append(self.entry_group)
        self.entry_group.add(self.entry_field)

        self.extension_selector = Adw.ComboRow()
        self.extension_selector.set_model(Gtk.StringList.new([".mp4", ".mov"]))
        self.extension_group = Adw.PreferencesGroup()
        self.entry_box.append(self.extension_group)
        self.extension_group.add(self.extension_selector)

        # combo row
        self.codecs_row = Adw.ComboRow()
        self.codecs_row.set_title("Codecs")
        self.codecs_row.set_model(Gtk.StringList.new(["H.264", "HEVC"]))

        self.codecs_row_group = Adw.PreferencesGroup()
        self.codecs_row_group.add(self.codecs_row)
        self.clamp_box.append(self.codecs_row_group)

        # converting button
        self.converting_box = Gtk.Box(spacing=10)
        self.clamp_box.append(self.converting_box)
        self.converting_button = Gtk.Button(label="Convert")
        self.converting_button.set_sensitive(False)
        self.converting_button.set_hexpand(True)
        self.converting_box.append(self.converting_button)
        self.converting_button.add_css_class("suggested-action")
        self.converting_button.add_css_class("pill")
        self.converting_button.set_margin_top(15)
        self.converting_button.connect(
            "clicked",
            File_dialog.file_dialog_save,
            self.main_window,
            self.file_dialog_result,
        )
        # preferences button (more options button)
        self.preferences_button = Gtk.Button(icon_name="open-menu-symbolic")
        self.preferences_button.set_valign(Gtk.Align.CENTER)
        self.preferences_button.set_margin_top(15)
        self.preferences_button.connect("clicked", self.show_preferences_dialog)
        self.converting_box.append(self.preferences_button)

    def on_entry_changed(self, entry_field):
        text = entry_field.get_text()
        not_allowed_chars = Ffmpeg.not_allowed_chars()
        if len(text) != 0:
            for char in text:
                if char not in not_allowed_chars:
                    self.converting_button.set_sensitive(True)
                else:
                    self.converting_button.set_sensitive(False)
                    break

        else:
            self.converting_button.set_sensitive(False)

    def get_selected_codec(self, _=""):
        selected_codec_index = self.codecs_row.get_selected()
        return self.codecs_row.get_model().get_string(selected_codec_index)

    def get_selected_extension(self, _=""):
        selected_extension_index = self.extension_selector.get_selected()
        return self.extension_selector.get_model().get_string(selected_extension_index)

    def get_page(self):
        return self.second_page

    def color_change(self, button):
        button.add_css_class("suggested-action")
        button.remove_css_class("dim-label")

    def file_dialog_result(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result).get_path()
            video_name = self.entry_field.get_text()
            input_video_path = self.main_page.video_path
            codec = self.get_selected_codec("")
            extension = self.get_selected_extension()

            self.progress_win = Progress_window(self.main_window)
            self.progress_win.present()
            thread = threading.Thread(
                target=self.run_the_converter,
                args=(input_video_path, folder, video_name, codec, extension),
            )
            thread.start()
        except GLib.GError:
            return

    def run_the_converter(self, video_path, folder, video_name, codec, extension):
        ffmpeg = Ffmpeg()
        ffmpeg.get_video_path(video_path)
        if codec == "H.264":
            codec = "libx264"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "h264_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension)
        elif codec == "HEVC":
            codec = "libx265"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "hevc_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension)
        else:
            codec = "libsvtav1"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "av1_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension)

    def show_preferences_dialog(self, _):
        self.preferences_dialog.present(self.main_window)


class Preferences_dialog(Adw.Dialog):
    def __init__(self, second_page):
        super().__init__(title="Preferences")
        self.second_page = second_page
        self.set_content_width(600)
        self.set_content_height(260)
        self.set_margin_bottom(20)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.set_child(self.main_box)

        self.headerbar = Adw.HeaderBar()
        self.headerbar.add_css_class("flat")
        self.main_box.append(self.headerbar)

        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(500)
        self.main_box.append(self.clamp)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.clamp.set_child(self.clamp_box)
        # switch rows

        self.settings_group = Adw.PreferencesGroup(title="Encoding Options")
        # hardware encoding siwtch row
        self.hardware_switch_row = Adw.SwitchRow(title="Hardware Encoding")
        self.settings_group.add(self.hardware_switch_row)
        self.hardware_switch_row.connect("notify::active", self.av1_option_visibility)
        # av1 software encoding siwtch row
        self.av1_switch_row = Adw.SwitchRow(title="AV1 Software Encoding")
        self.settings_group.add(self.av1_switch_row)
        self.clamp_box.append(self.settings_group)

        # alert dialog
        self.alert_dialog = Adw.AlertDialog(
            heading="Enable AV1 Software Encoding?",
            body="AV1 Software Encoding It May Be Very Slow On Some Devices",
            default_response="Cancel",
            close_response="Cancel",
        )
        self.alert_dialog.add_response("Cancel", "Cancel")
        self.alert_dialog.add_response("Enable", "Enable")
        self.alert_dialog.set_response_appearance(
            "Enable", Adw.ResponseAppearance.DESTRUCTIVE
        )
        self.alert_dialog.connect("response", self.alert_dialog_response)
        self.av1_switch_row.connect("notify::active", self.av1_switch_row_enabled)

    def av1_switch_row_senstive(self):
        if self.hardware_switch_row.get_active():
            self.av1_switch_row.set_sensitive(False)

        else:
            self.av1_switch_row.set_sensitive(True)

    def av1_option_visibility(self, _="", _2=""):
        if self.av1_switch_row.get_active() or self.hardware_switch_row.get_active():
            self.second_page.combo_row.set_model(
                Gtk.StringList.new(["H.264", "HEVC", "AV1"])
            )
            self.av1_switch_row_senstive()

        else:
            self.second_page.combo_row.set_model(Gtk.StringList.new(["H.264", "HEVC"]))
            self.av1_switch_row_senstive()

    def av1_switch_row_enabled(self, _, _2):
        if self.av1_switch_row.get_active():
            self.alert_dialog.choose(parent=self.second_page.main_window)
        self.av1_option_visibility()

    def alert_dialog_response(self, dialog, response):
        if response == "Cancel":
            self.av1_switch_row.set_active(False)


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

    def convert_video(self, window, codec, folder, video_name, extension):
        process = subprocess.Popen(
            f"ffmpeg -y -i {self.video_path} -c:v {codec} -c:a copy {folder}/{video_name}{extension}",
            shell=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in process.stderr:
            if (
                self.cancel_process(
                    process, window.progress_win, folder, video_name, extension
                )
                == "done"
            ):
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

    def cancel_process(self, process, progress_win, folder, video_name, extension):
        if progress_win.cancellation:
            GLib.idle_add(progress_win.process_end)
            process.kill()
            subprocess.run(f"rm {folder}/{video_name}{extension}", shell=True)
            return "done"

    @staticmethod
    def not_allowed_chars():
        not_allowed_chars = list(string.punctuation)
        not_allowed_chars.append(" ")
        return Ffmpeg.delete_allowed_chars(not_allowed_chars)

    @staticmethod
    def delete_allowed_chars(lis):
        lis.remove(",")
        lis.remove("^")
        allowed_chars = ["+", "~", "^", "@", "-", "_", ",", "=", "[", "]"]
        for char in lis:
            print(char)
            if char in allowed_chars:
                lis.remove(char)
        return lis
