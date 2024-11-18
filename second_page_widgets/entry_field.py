import gi
gi.require_versions({"Gtk":"4.0","Adw":"1"})
from gi.repository import Adw, Gtk

class Entry_field:
    def __init__(self,box, on_entry_change_function):
        self.entry_box = Gtk.Box(spacing=6)
        box.append(self.entry_box)

        self.entry_field = Adw.EntryRow()
        # self.entry_field.set_max_length(30)
        self.entry_field.connect("changed", on_entry_change_function)
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
