from second_page_widgets.entry_field import Entry_field
from second_page_widgets.video_settings import Video_settings
from second_page_widgets.converting_button import Converting_button
from second_page_widgets.preferences_button import Preferences_button
from second_page_widgets.progress_window import Progress_window
from second_page_widgets.preferences_dialog import Preferences_dialog
import re
import subprocess
import string
import threading
from file_dialog import File_dialog
import gi


from gi.repository import Adw, GLib, Gtk



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

        self.entry_field = Entry_field(self.clamp_box, self.on_entry_changed)

        self.video_settings = Video_settings(self.clamp_box)

        # converting button
        self.converting_box = Gtk.Box(spacing=10)
        self.clamp_box.append(self.converting_box)
        self.converting_button = Converting_button(self.converting_box, self.main_window, self.file_dialog_result)

        # preferences button (more options button)
        self.preferences_button = Preferences_button(self.converting_box, self.show_preferences_dialog)

    def on_entry_changed(self,_):
        text = self.entry_field.entry_field.get_text()
        not_allowed_chars = Ffmpeg.not_allowed_chars()
        if len(text) != 0:
            for char in text:
                if char not in not_allowed_chars:
                    self.converting_button.converting_button.set_sensitive(True)
                else:
                    self.converting_button.converting_button.set_sensitive(False)
                    break

        else:
            self.converting_button.converting_button.set_sensitive(False)

    def get_selected_codec(self, _=""):
        selected_codec_index = self.video_settings.codecs_row.get_selected()
        return self.video_settings.codecs_row.get_model().get_string(selected_codec_index)

    def get_selected_extension(self, _=""):
        selected_extension_index = self.entry_field.extension_selector.get_selected()
        return self.entry_field.extension_selector.get_model().get_string(selected_extension_index)

    def get_selected_quality(self,_=""):
        selected_quality_index = self.video_settings.video_quality_row.get_selected()
        quality_dict_key = self.video_settings.video_quality_row.get_model().get_string(selected_quality_index)
        return self.video_settings.video_quality_dict[quality_dict_key]

    def get_page(self):
        return self.second_page

    def color_change(self, button):
        button.add_css_class("suggested-action")
        button.remove_css_class("dim-label")

    def file_dialog_result(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result).get_path()
            video_name = self.entry_field.entry_field.get_text()
            input_video_path = self.main_page.video_path
            codec = self.get_selected_codec()
            extension = self.get_selected_extension()
            quality = self.get_selected_quality()

            self.progress_win = Progress_window(self.main_window)
            self.progress_win.present()
            thread = threading.Thread(
                target=self.run_the_converter,
                args=(input_video_path, folder, video_name, codec, extension, quality),
            )
            thread.start()
        except GLib.GError:
            return

    def run_the_converter(self, video_path, folder, video_name, codec, extension, quality):
        ffmpeg = Ffmpeg()
        ffmpeg.get_video_path(video_path)
        if codec == "H.264":
            codec = "libx264"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "h264_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension, quality)
        elif codec == "HEVC":
            codec = "libx265"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "hevc_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension, quality)
        else:
            codec = "libsvtav1"
            if self.preferences_dialog.hardware_switch_row.get_active():
                codec = "av1_nvenc"
            ffmpeg.convert_video(self, codec, folder, video_name, extension, quality)

    def show_preferences_dialog(self, _):
        self.preferences_dialog.present(self.main_window)


class Ffmpeg:
    def __ini__(self):
        self.video_path = None
        self.duration = None

    def convert_video(self, window, codec, folder, video_name, extension, quality):
        process = subprocess.Popen(
            f"ffmpeg -y -i {self.video_path} -c:v {codec} -c:a copy -crf {quality} {folder}/{video_name}{extension}",
            shell=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in process.stderr:
            print(line)
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
            if char in allowed_chars:
                lis.remove(char)
        return lis
