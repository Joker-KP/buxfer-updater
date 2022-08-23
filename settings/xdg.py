import shutil
import subprocess


class XdgDirs:
    """Get user directories with system tool 'xdg-user-dir'"""
    def __init__(self):
        self.xdg_bin = shutil.which('xdg-user-dir')

    def get_folder(self, name='DOWNLOAD'):
        process = subprocess.run([self.xdg_bin, name], stdout=subprocess.PIPE)
        path = process.stdout.strip().decode()
        return path
