import logging
import os
from datetime import datetime

import yaml


class History:
    filename = None
    accounts = dict()

    def __init__(self, history_file='data/history.yaml'):
        self.filename = history_file
        if os.path.exists(history_file):
            with open(history_file, 'r') as file:
                self.accounts = yaml.safe_load(file)
        else:
            self.update()

    def update(self, account_id=None, name=None, value=None):
        if account_id and account_id not in self.accounts:
            self.accounts[account_id] = dict()
        if account_id and name:
            if isinstance(value, datetime):
                value = f'{value:%Y-%m-%d %H:%M:%S}'
            self.accounts[account_id][name] = value
        logging.debug('Updating history file')
        with open(self.filename, 'w') as f:
            yaml.dump(self.accounts, f, sort_keys=False, default_flow_style=False)

    def log_start(self, account_id, folder_name, parser_identifier):
        self.update(account_id, 'name', folder_name.strip())
        self.update(account_id, 'parser', parser_identifier)
        self.update(account_id, 'last_start', datetime.now())

    def log_download_result(self, account_id, is_ok, status_msg, basename):
        if is_ok:
            self.update(account_id, 'last_download_success', datetime.now())
            self.update(account_id, 'last_download_success_file', basename)
        else:
            self.update(account_id, 'last_download_failure', datetime.now())
            self.update(account_id, 'last_download_failure_msg', status_msg)

    def log_upload_result(self, account_id, is_ok, status_msg, basename):
        if is_ok:
            self.update(account_id, 'last_upload_success', datetime.now())
            self.update(account_id, 'last_upload_success_file', basename)
        else:
            self.update(account_id, 'last_upload_failure', datetime.now())
            self.update(account_id, 'last_upload_failure_msg', status_msg)
            self.update(account_id, 'last_upload_failure_file', basename)
