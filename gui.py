"""GTK GUI for SwayCap"""

import sys
import subprocess
from pathlib import Path

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
except ImportError:
    print("Error: GTK3 not available. Install python3-gobject")
    sys.exit(1)

from . import capture
from .config import get_config

class SwayCapWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="SwayCap")
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.add(vbox)

        self.mode_label = Gtk.Label(label="Capture Mode")
        vbox.pack_start(self.mode_label, False, False, 0)

        mode_box = Gtk.Box(spacing=10)
        vbox.pack_start(mode_box, False, False, 0)

        self.screenshot_radio = Gtk.RadioButton(label="Screenshot")
        self.screenshot_radio.connect("toggled", self.on_mode_changed, "screenshot")
        mode_box.pack_start(self.screenshot_radio, False, False, 0)

        self.video_radio = Gtk.RadioButton(label="Video", group=self.screenshot_radio)
        self.video_radio.connect("toggled", self.on_mode_changed, "video")
        mode_box.pack_start(self.video_radio, False, False, 0)

        method_label = Gtk.Label(label="Capture Method")
        vbox.pack_start(method_label, False, False, 0)

        self.method_combo = Gtk.ComboBoxText()
        self.method_combo.append("fullscreen", "Full Screen")
        self.method_combo.append("window", "Active Window")
        self.method_combo.append("area", "Drag Area")
        self.method_combo.set_active(0)
        vbox.pack_start(self.method_combo, False, False, 0)

        self.capture_btn = Gtk.Button(label="Capture")
        self.capture_btn.connect("clicked", self.on_capture_clicked)
        self.capture_btn.set_size_request(200, 50)
        vbox.pack_start(self.capture_btn, False, False, 10)

        self.status_label = Gtk.Label(label="Ready")
        vbox.pack_start(self.status_label, False, False, 0)

        self.screenshot_radio.set_active(True)
        self.update_method_options()
        self.update_button_state()

    def on_mode_changed(self, button, mode):
        self.method_combo.set_active(0)
        self.update_method_options()
        self.update_button_state()

    def update_method_options(self):
        model = self.method_combo.get_model()
        model.clear()

        if self.screenshot_radio.get_active():
            self.method_combo.append("fullscreen", "Full Screen")
            self.method_combo.append("window", "Active Window")
            self.method_combo.append("area", "Drag Area")
        else:
            self.method_combo.append("fullscreen", "Full Screen")
            self.method_combo.append("area", "Drag Area")

        self.method_combo.set_active(0)

    def update_button_state(self):
        is_recording = capture.is_recording()
        if is_recording:
            self.capture_btn.set_label("Stop Recording")
        else:
            if self.video_radio.get_active():
                self.capture_btn.set_label("Start Recording")
            else:
                self.capture_btn.set_label("Capture")

    def on_capture_clicked(self, button):
        is_recording = capture.is_recording()

        if is_recording:
            capture.stop_recording()
            self.status_label.set_label("Recording stopped")
            self.update_button_state()
            return

        mode = "video" if self.video_radio.get_active() else "screenshot"
        method = self.method_combo.get_active_id()

        self.status_label.set_label(f"Capturing {mode} ({method})...")
        self.capture_btn.set_sensitive(False)

        try:
            if mode == "screenshot":
                result = capture.screenshot(method)
                if result:
                    self.status_label.set_label(f"Saved: {Path(result).name}")
                else:
                    self.status_label.set_label("Capture cancelled")
            else:
                result = capture.video(method)
                if result:
                    self.status_label.set_label(f"Recording to: {Path(result).name}")
                    self.update_button_state()
                    self.capture_btn.set_sensitive(True)
                    return
                else:
                    self.status_label.set_label("Recording cancelled")
        except Exception as e:
            self.status_label.set_label(f"Error: {e}")

        self.capture_btn.set_sensitive(True)

def main():
    app = SwayCapWindow()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()