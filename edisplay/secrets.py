import os

import yaml


CONFIG_FILE = os.path.join('secrets.yaml')
CONFIG = None


def get_secret(section, key=None):
    global CONFIG
    if CONFIG is None:
        with open(CONFIG_FILE, 'r') as file:
            CONFIG = yaml.safe_load(file)

    if key is not None:
        section_found = CONFIG.get(section)
        return section_found.get(key)

    return CONFIG.get(section)
