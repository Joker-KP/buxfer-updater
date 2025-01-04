import os.path
import re


class MozillaSettings:
    """Read entries from Mozilla prefs.js file"""

    def __init__(self, preferences_file=None):
        if preferences_file is None:
            paths = ["~/.mozilla/firefox/", "~/snap/firefox/common/.mozilla/firefox/"]
            for path in paths:
                profiles_file = os.path.expanduser(path + "profiles.ini")
                if os.path.isfile(profiles_file):
                    with open(profiles_file, "r") as f:
                        content = f.read().splitlines()
                        for line in content:
                            matches = re.match(r'Default=(\w+.+)', line)
                            if matches:
                                self.file = os.path.join(os.path.expanduser(path), matches[1], "prefs.js")
                                return
                    with open(profiles_file, "r") as f:
                        content = f.read().splitlines()
                        for line in content:
                            matches = re.match(r'Path=(\w+.+)', line)
                            if matches:
                                self.file = os.path.join(os.path.expanduser(path), matches[1], "prefs.js")
                                return
        else:
            self.file = preferences_file

    def read_key(self, key):
        """Read value from file. If not exist return None"""
        with open(self.file, "rt", encoding="utf-8") as f:
            content = f.read().splitlines()
        for line in content:
            matches = re.match(r'^user_pref\(\s*"{0}"\s*,\s*"?([^\"]*)"?\);\s*$'.format(key), line)
            if matches:
                return str(matches[1])
        return None
