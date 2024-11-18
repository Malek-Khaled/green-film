import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

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
            self.second_page.video_settings.codecs_row.set_model(
                Gtk.StringList.new(["H.264", "HEVC", "AV1"])
            )
            self.av1_switch_row_senstive()

        else:
            self.second_page.video_settings.codecs_row.set_model(Gtk.StringList.new(["H.264", "HEVC"]))
            self.av1_switch_row_senstive()

    def av1_switch_row_enabled(self, _, _2):
        if self.av1_switch_row.get_active():
            self.alert_dialog.choose(parent=self.second_page.main_window)
        self.av1_option_visibility()

    def alert_dialog_response(self, _, response):
        if response == "Cancel":
            self.av1_switch_row.set_active(False)

