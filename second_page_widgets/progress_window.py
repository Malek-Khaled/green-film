import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk


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



