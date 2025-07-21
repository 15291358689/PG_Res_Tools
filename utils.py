import os
import re

def find_config_json(source):
    config_files = []
    pattern = re.compile(r'^config\.[a-f0-9]+\.json$', re.IGNORECASE)
    for root, _, files in os.walk(source):
        for file in files:
            if pattern.match(file):
                config_files.append(os.path.join(root, file))
    return config_files