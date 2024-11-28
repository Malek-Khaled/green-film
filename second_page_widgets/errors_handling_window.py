import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

class Errors_handling_window(Adw.Window):
    def __init__(self, parent):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("No Encoder found")
        self.set_default_size(400, 200)

        # main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_content(self.main_box)

        # center box
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_hexpand(True)
        self.center_box.set_vexpand(True)
        self.main_box.append(self.center_box)

        # label
        self.error_label = Gtk.Label()
        self.error_label.set_wrap(True)
        self.center_box.append(self.error_label)

        # close button
        self.close_button = Gtk.Button(label="Close")
        self.close_button.add_css_class("destructive-action")
        self.close_button.connect("clicked", self.close_Window)
        self.close_button.set_margin_bottom(20)
        # button clamp
        self.close_button_clamp = Adw.Clamp()
        self.close_button_clamp.set_maximum_size(200)
        self.main_box.append(self.close_button_clamp)
        self.close_button_clamp.set_child(self.close_button)

    def no_encoder_found_present(self):
        self.error_label.add_css_class("title-3")
        self.error_label.set_label("There Is No Encoder Found")
        self.present()

    def no_hardware_decoder_found_present(self):
        self.error_label.set_max_width_chars(30)
        self.error_label.add_css_class("title-4")
        self.error_label.set_label(
            "There Is No Hardware Acceleration Support On Your Card"
        )
        self.present()

    def ffmpeg_not_found(self):
        self.error_label.add_css_class("title-3")
        self.error_label.set_label("FFmpeg Is Not installed")
        self.present()

    def close_Window(self, _):
        self.hide()
        self.destroy()
