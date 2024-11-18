import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

class Video_settings:
    def __init__(self, box):
            # Video settings group
            self.video_settings_group = Adw.PreferencesGroup()
            # Codecs
            self.codecs_row = Adw.ComboRow()
            self.codecs_row.set_title("Codecs")
            self.codecs_row.set_model(Gtk.StringList.new(["H.264", "HEVC"]))
            # Video quality
            self.video_quality_row = Adw.ComboRow()
            self.video_quality_row.set_title("Quality")
            self.video_quality_dict = {"Low":30,"Medium":20,"High":10,"Lossless":0}
            self.video_quality_row.set_model(Gtk.StringList.new(list(self.video_quality_dict.keys())))

            self.video_settings_group.add(self.codecs_row)
            self.video_settings_group.add(self.video_quality_row)
            box.append(self.video_settings_group)




