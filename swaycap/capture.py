"""Capture functionality using grim and wf-recorder"""

import subprocess
import os
import signal
from datetime import datetime
from pathlib import Path
from .config import get_config, get_default_save_dir

_recording_pid = None

def _get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path

def _notify(title, message):
    config = get_config()
    if config.get_bool('general', 'notification', True):
        subprocess.run(['notify-send', title, message], check=False)

def _get_focused_window():
    try:
        result = subprocess.run(
            ['swaymsg', '-t', 'get_tree'],
            capture_output=True, text=True, check=True
        )
        import json
        tree = json.loads(result.stdout)
        return _find_focused_window(tree)
    except Exception:
        return None

def _find_focused_window(node):
    if node.get('focused'):
        return node.get('id')
    for child in node.get('nodes', []) + node.get('floating_nodes', []):
        result = _find_focused_window(child)
        if result:
            return result
    return None

def screenshot(capture_type='fullscreen', output_path=None, post_action=None):
    config = get_config()

    if capture_type == 'fullscreen':
        cmd = ['grim']
    elif capture_type == 'window':
        window_id = _get_focused_window()
        if not window_id:
            _notify("Screenshot failed", "No focused window found")
            return None
        cmd = ['grim', '-T', str(window_id)]
    elif capture_type == 'area':
        geom = subprocess.run(['slurp'], capture_output=True, text=True)
        if not geom.stdout.strip():
            return None
        cmd = ['grim', '-g', geom.stdout.strip()]
    else:
        raise ValueError(f"Unknown capture type: {capture_type}")

    format_ext = config.get('screenshot', 'format', 'png')
    save_dir = config.get('screenshot', 'save_directory')
    if save_dir:
        save_dir = Path.home() / save_dir
    else:
        save_dir = get_default_save_dir('screenshot')
    _ensure_dir(save_dir)

    if post_action is None:
        post_action = config.get('screenshot', 'post_action', 'both')

    filename = f"screenshot_{_get_timestamp()}.{format_ext}"
    filepath = save_dir / filename

    if post_action in ('directory', 'both'):
        cmd.append(str(filepath))

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        _notify("Screenshot failed", str(e))
        return None

    if post_action in ('clipboard', 'both'):
        if post_action == 'clipboard':
            subprocess.run(['wl-copy'], input=result.stdout, check=False)
        else:
            with open(filepath, 'rb') as f:
                subprocess.run(['wl-copy'], input=f.read(), check=False)

    _notify("Screenshot saved", str(filepath) if post_action in ('directory', 'both') else "Copied to clipboard")
    return str(filepath) if post_action in ('directory', 'both') else None

def video(capture_type='fullscreen', output_path=None, post_action=None):
    global _recording_pid

    wf_recorder_path = subprocess.run(['which', 'wf-recorder'], capture_output=True).stdout
    if not wf_recorder_path.strip():
        _notify("Recording failed", "wf-recorder not installed. Run: sudo dnf install wf-recorder")
        return None

    config = get_config()

    if capture_type == 'fullscreen':
        cmd = ['wf-recorder']
    elif capture_type == 'area':
        geom = subprocess.run(['slurp'], capture_output=True, text=True)
        if not geom.stdout.strip():
            return None
        cmd = ['wf-recorder', '-g', geom.stdout.strip()]
    else:
        raise ValueError(f"Unknown capture type: {capture_type}")

    format_ext = config.get('video', 'format', 'mp4')
    save_dir = config.get('video', 'save_directory')
    if save_dir:
        save_dir = Path.home() / save_dir
    else:
        save_dir = get_default_save_dir('video')
    _ensure_dir(save_dir)

    if post_action is None:
        post_action = config.get('video', 'post_action', 'directory')

    filename = f"video_{_get_timestamp()}.{format_ext}"
    filepath = save_dir / filename

    cmd.extend(['-f', str(filepath)])

    try:
        proc = subprocess.Popen(cmd)
        _recording_pid = proc.pid
        _notify("Recording started", f"Saving to {filepath}")
        return str(filepath)
    except Exception as e:
        _notify("Recording failed", str(e))
        return None

def stop_recording():
    global _recording_pid

    if _recording_pid is None:
        _notify("No recording", "No active recording to stop")
        return False

    try:
        os.kill(_recording_pid, signal.SIGTERM)
        _recording_pid = None
        _notify("Recording stopped", "Video saved successfully")
        return True
    except ProcessLookupError:
        _recording_pid = None
        _notify("No recording", "Process not found")
        return False
    except Exception as e:
        _recording_pid = None
        _notify("Stop failed", str(e))
        return False

def is_recording():
    global _recording_pid
    if _recording_pid is None:
        return False
    try:
        os.kill(_recording_pid, 0)
        return True
    except ProcessLookupError:
        _recording_pid = None
        return False