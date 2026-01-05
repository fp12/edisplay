import configparser
import os
from typing import Dict


CONFIG_FILE = os.path.join('secrets.ini')
CONFIG = configparser.ConfigParser()


if os.path.exists(CONFIG_FILE):
    CONFIG.read(CONFIG_FILE)
else:
    print(f"Warning: Configuration file not found at {CONFIG_FILE}")


def get_config(section, option, fallback=None) -> Dict:
    return CONFIG.get(section, option, fallback=fallback)
