from project.settings_global import *

try:
    from project.settings_local import *
except ImportError:
    print('Failed to load local settings! Make sure settings_local file is present.')
    exit(1)

