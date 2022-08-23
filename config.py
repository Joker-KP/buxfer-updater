import os

import cryptocode
import yaml

from settings.settings import get_ff_binary, get_ff_download_dir


class Configuration:
    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

        self.account_data_dir = self.get_key('general', 'account_data_dir', 'data')
        self.folder_filter = self.get_key('general', 'folder_filter', '')
        self.no_download = self.get_key('general', 'no_download', False)
        self.no_upload = self.get_key('general', 'no_upload', False)
        self.browser_bin = self.get_key('browser', 'exec', get_ff_binary())
        self.browser_download_dir = self.get_key('browser', 'download_dir', get_ff_download_dir())
        self.ui_vision_init_html = os.path.abspath(self.get_key('uivision', 'init_file', 'uivision/ui.vision.html'))
        self.ui_vision_file_storage = self.get_key('uivision', 'use_file_storage', True)
        self.ui_vision_account_timeout = self.get_key('uivision', 'account_timeout', 60)
        self.ui_vision_keep_logs = self.get_key('uivision', 'keep_logs', True)
        self.salt = self.get_key('security', 'salt', os.getcwd())

    def get_key(self, primary_key, secondary_key, default_value):
        if primary_key in self.config:
            if secondary_key in self.config[primary_key]:
                value = self.config[primary_key][secondary_key]
                return value if value != "" else default_value
        return default_value


def update_secrets(passphrase, salt):
    encoded = cryptocode.encrypt(passphrase, salt)
    username, _ = buxfer_auth_data(salt)
    secrets = {'buxfer_account': {'login': username, 'password': encoded}}
    with open('secrets.yaml', 'w') as f:
        yaml.dump(secrets, f, sort_keys=False, default_flow_style=False)
    return encoded


def buxfer_auth_data(salt):
    with open('secrets.yaml', 'r') as file:
        data = yaml.safe_load(file)
    if 'buxfer_account' not in data:
        print("Missing username and password in secrets.yaml")
        return None, None
    user = data['buxfer_account']['login']
    encoded_pass = data['buxfer_account']['password']
    return user, cryptocode.decrypt(encoded_pass, salt)