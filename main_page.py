import os
import gi
from second_page import Second_page

from gi.repository import Adw, Gtk

absolute_path = os.path.dirname(__file__)


class Main_page:
    def __init__(self, main_window):
        self.main_window = main_window
        self.first_page = Adw.NavigationPage()
        self.first_page.set_title("Green Film")
        self.video_path = ""
        self.video_name = ""

        # main box

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)

        # center box
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.center_box.set_hexpand(True)
        self.center_box.set_vexpand(True)

        # header bar
        self.headerbar = Adw.HeaderBar()
        self.main_box.append(self.headerbar)
        self.headerbar.add_css_class("flat")

        # clamp
        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(400)
        self.clamp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # add
        self.main_box.append(self.center_box)
        self.clamp.set_child(self.clamp_box)
        self.center_box.append(self.clamp)

        # Logo
        self.logo_path = absolute_path + "/greenfilm-logo.svg"
        self.app_logo = Gtk.Image()
        self.app_logo.set_from_file(self.logo_path)
        self.app_logo.set_pixel_size(150)
        self.app_logo.set_margin_bottom(25)
        self.app_logo.add_css_class("icon-dropshadow")
        self.clamp_box.append(self.app_logo)

        # input group
        self.group = Adw.PreferencesGroup()
        # button
        self.import_file_button = Gtk.Button(label="Add a Video")
        self.import_file_button.add_css_class("suggested-action")
        self.import_file_button.add_css_class("pill")
        self.import_file_button.set_margin_top(25)
        self.import_file_button.connect("clicked", self.file_dialog_open)

        # app name label
        self.app_name_label = Gtk.Label(label="Green Film")
        self.app_name_label.add_css_class("title-1")
        self.app_name_label.set_margin_bottom(5)

        # app description label
        self.description_label = Gtk.Label(label="Add A Video To Start Converting")

        # add widgets to preferences group
        # self.group.add(self.combo_row)
        self.group.add(self.app_name_label)
        self.group.add(self.description_label)
        self.group.add(self.import_file_button)
        self.clamp_box.append(self.group)

        self.first_page.set_child(self.main_box)

    def file_dialog_open(self, _):
        file_dialog = Gtk.FileChooserDialog(
            title="Choose a video",
            parent=self.main_window,
            action=Gtk.FileChooserAction.OPEN,
        )
        file_dialog.set_size_request(800, 600)

        file_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        file_dialog.add_button("Open", Gtk.ResponseType.ACCEPT).add_css_class(
            "suggested-action"
        )

        # add filter
        filter = Gtk.FileFilter()
        filter.add_pattern("*.mp4")
        filter.add_pattern("*.mov")
        file_dialog.add_filter(filter)
        file_dialog.connect("response", self.file_dialog_responce)
        file_dialog.present()
        self.import_file_button.set_sensitive(False)

    def file_dialog_responce(self, dialog, responce):
        if responce == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            file_name = dialog.get_file().get_basename()
            self.video_path = file_path
            self.video_name = file_name
            dialog.destroy()
            second_page = Second_page(self, self.main_window).get_page()
            self.main_window.navigation_view.push(second_page)

        dialog.destroy()
        self.import_file_button.set_sensitive(True)

    def get_the_page(self):
        return self.first_page
