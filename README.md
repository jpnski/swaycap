# SwayCap

A simple GUI/CLI screen recorder for Sway/Wayland.

## Features

- GUI and CLI interfaces
- Screenshot capture: full screen, active window, or drag area selection
- Video recording: full screen or drag area selection
- Configurable via `~/.config/swaycap/swaycap.conf`
- Copy to clipboard or save to disk (configurable)
- Notifications on capture completion

## Requirements

### Fedora

```bash
sudo dnf install grim wl-copy slurp wf-recorder python3-gobject python3-cairo
```

- `grim`: Screenshot capture
- `wl-copy`: Clipboard operations
- `slurp`: Area selection
- `wf-recorder`: Video recording
- `python3-gobject`, `python3-cairo`: GUI support

### Arch

```bash
sudo pacman -S grim wl-clipboard slurp wf-recorder python-gobject python-cairo
```

## Installation

```bash
pip install .
```

This installs the `swaycap` CLI command and `swaycap-gui` GUI command.

## Configuration

The configuration file is located at `~/.config/swaycap/swaycap.conf`. It is created automatically on first run with default values.

### Config Options

```ini
[general]
notification = true          # Show notifications on capture

[screenshot]
format = png                 # Image format: png, jpeg
quality = highest            # Image quality (for jpeg): 0-100 or highest
save_directory = Pictures/Screenshots  # Save directory (relative to home)
# post_action options: directory, clipboard, both
post_action = both           # Save to directory and/or copy to clipboard

[video]
format = mp4                 # Video format (determined by extension)
resolution = highest        # Resolution setting
save_directory = Videos/Recordings    # Save directory
# post_action options: directory, notify_only
post_action = directory     # Save to directory
```

## Usage

### GUI

Launch the graphical interface:

```bash
swaycap gui
```

The GUI provides:
- Mode toggle: Screenshot / Video
- Capture method: Full Screen, Active Window (screenshot only), Drag Area
- Capture button

### CLI

Capture a screenshot:

```bash
# Full screen
swaycap capture --screenshot --fullscreen

# Active window
swaycap capture --screenshot --window

# Drag area
swaycap capture --screenshot --area
```

Record a video:

```bash
# Full screen
swaycap capture --video --fullscreen

# Drag area
swaycap capture --video --area
```

Stop recording:

```bash
swaycap capture --stop
# or
swaycap stop
```

## Sway Keybinds

Add to your Sway config (`~/.config/sway/config`):

```
# Screenshot
bindsym Mod+Shift+p exec swaycap capture --screenshot --fullscreen
bindsym Mod+Shift+s exec swaycap capture --screenshot --area
bindsym Mod+Shift+w exec swaycap capture --screenshot --window

# Video recording
bindsym Mod+Shift+r exec swaycap capture --video --fullscreen
bindsym Mod+Shift+v exec swaycap capture --video --area

# Stop recording
bindsym Mod+Shift+m exec swaycap capture --stop
```

## License

MIT License
