import hashlib
import os
import re
import sys

import clize

from buxfer.api import Buxfer
from buxfer.filters import filter_content
from config import Configuration, buxfer_auth_data, update_secrets
from uivision.launcher import download_statement


def md5(file_path: str):
    with open(file_path, "rb") as file:
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_account_folders(account_data_dir: str):
    result = []
    pattern = r'([^\[]+)\[([\d]+);([^\]]+)]$'
    for entry in os.listdir(account_data_dir):
        if os.path.isdir(account_data_dir + '/' + entry):
            matches = re.match(pattern, entry)
            if matches:
                result += [{'entry': entry,
                            'name': matches[1],
                            'account_id': matches[2],
                            'filter': matches[3]}]
    return result


def folders_walk(buxfer_api, config):
    folders = get_account_folders(config.account_data_dir)
    for folder in folders:
        account_id = folder['account_id']
        extension_filter = folder['filter']
        print(f"Folder check: {folder['name']} (id: {account_id}, format: {extension_filter})")

        account_folder = f"{config.account_data_dir}/{folder['entry']}"
        download_statement(account_folder, account_id, config)

        md5file = f"{account_folder}/md5s.txt"
        md5content = ""
        if os.path.exists(md5file):
            with open(md5file, "r") as file:
                md5content = file.read()
        md5orig = md5content

        for entry in os.listdir(f"{account_folder}"):
            statement_file = f"{account_folder}/{entry}"
            if os.path.isfile(statement_file) and entry != "md5s.txt":
                md5hash = md5(statement_file)
                if md5hash not in md5content:
                    print(f"-- Uploading {entry}...", end='')
                    statement_content = filter_content(statement_file, extension_filter)
                    if buxfer_api.upload_statement(account_id, statement_content):
                        # // if ok -> keep md5 (no further uploads of this file)
                        print("OK")
                        md5content += f"{md5hash}\n"

        if md5orig != md5content:
            with open(md5file, "w") as file:
                file.write(md5content)


def main(*,
         updated_buxfer_password: str = None,
         ):
    """
    Gather statements (history of transactions) from online bank accounts (using UI Vision RPA).
    Possibly preprocess and upload these files to buxfer.com for further transactions analysis.

    :param updated_buxfer_password: password to be encoded (with salt) and stored in secrets.yaml
    """
    config = Configuration()

    if updated_buxfer_password:
        update_secrets(updated_buxfer_password, config.salt)
        return

    print('Started...')
    username, password = buxfer_auth_data(config.salt)
    buxfer_api = Buxfer(username, password)
    if buxfer_api.is_logged_in():
        folders_walk(buxfer_api, config)


if __name__ == '__main__':
    if not sys.version_info >= (3, 5):
        print("Older platforms may not work correctly with this code.\n"
              "The solution was developed using Python 3.9.\n"
              "Please, consider an update.")

    clize.run(main)
