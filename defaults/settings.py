import shutil

from .mozilla import MozillaSettings
from .xdg import XdgDirs


def get_ff_download_dir():
    result = None
    mozilla = MozillaSettings()
    xdg = XdgDirs()
    ff_option = mozilla.read_key("browser.download.folderList")
    if ff_option is not None:
        ff_option = int(ff_option)
        if ff_option == 0:
            result = xdg.get_folder('DESKTOP')
        elif ff_option == 1:
            result = xdg.get_folder('DOWNLOAD')
        elif ff_option == 2:
            result = mozilla.read_key("browser.download.dir")
    else:
        result = xdg.get_folder('DOWNLOAD')
    return result


def get_ff_binary():
    return shutil.which('firefox')
