"""Configuration handling for SwayCap"""

import os
import configparser
from pathlib import Path

DEFAULT_CONFIG = """[general]
notification = true

[screenshot]
format = png
quality = highest
save_directory = Pictures/Screenshots
post_action = both

[video]
format = mp4
resolution = highest
save_directory = Videos/Recordings
post_action = directory
"""

class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path or self._get_config_path()
        self.parser = configparser.ConfigParser()
        self._load()

    def _get_config_path(self):
        xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        return Path(xdg_config) / 'swaycap' / 'swaycap.conf'

    def _load(self):
        if not self.config_path.exists():
            self._create_default()

        self.parser.read(self.config_path)

        if not self.parser.has_section('general'):
            self.parser.add_section('general')
        if not self.parser.has_section('screenshot'):
            self.parser.add_section('screenshot')
        if not self.parser.has_section('video'):
            self.parser.add_section('video')

    def _create_default(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            f.write(DEFAULT_CONFIG)

    def get(self, section, key, fallback=None):
        try:
            return self.parser.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_bool(self, section, key, fallback=False):
        val = self.get(section, key, str(fallback))
        return val.lower() in ('true', 'yes', '1', 'on')

    def reload(self):
        self.parser.read(self.config_path)

def get_default_save_dir(media_type):
    home = Path.home()
    if media_type == 'screenshot':
        return home / 'Pictures' / 'Screenshots'
    elif media_type == 'video':
        return home / 'Videos' / 'Recordings'
    return home

def get_config():
    return Config()