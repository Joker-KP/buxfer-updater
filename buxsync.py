import hashlib
import os
import re
import sys

import clize

from buxfer.api import Buxfer
from buxfer.reader_selector import read_content
from config import Configuration, buxfer_auth_data, update_secrets
from uivision.launcher import download_statement


def md5(file_path: str):
    with open(file_path, "rb") as file:
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_account_folders(account_data_dir: str, folder_filter = ''):
    result = []
    pattern = r'([^\[]+)\[([\d]+);([^\]]+)]$'
    for entry in os.listdir(account_data_dir):
        if folder_filter and folder_filter not in entry:
            continue
        if os.path.isdir(account_data_dir + '/' + entry):
            matches = re.match(pattern, entry)
            if matches:
                result += [{'entry': entry,
                            'name': matches[1],
                            'account_id': matches[2],
                            'reader_id': matches[3]}]
    return result


def folders_walk(buxfer_api, config):
    folders = get_account_folders(config.account_data_dir, config.folder_filter)
    for folder in folders:
        account_id = folder['account_id']
        parser_identifier = folder['reader_id']
        print(f"Folder check: {folder['name']} (id: {account_id}, format: {parser_identifier})")

        account_folder = f"{config.account_data_dir}/{folder['entry']}"
        if not config.no_download:
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
                    statement_content = read_content(statement_file, parser_identifier)
                    if not config.no_upload:
                        print(f"-- Uploading {entry}...", end='')
                        if buxfer_api.upload_statement(account_id, statement_content):
                            # // if ok -> keep md5 (no further uploads of this file)
                            print("OK")
                            md5content += f"{md5hash}\n"

        if md5orig != md5content:
            with open(md5file, "w") as file:
                file.write(md5content)


def main(*,
         folder_filter: str = '',
         no_download: bool = False,
         no_upload: bool = False,
         updated_buxfer_password: str = None
         ):
    """
    Gather statements (history of transactions) from online bank accounts (using UI Vision RPA).
    Possibly preprocess and upload these files to buxfer.com for further transactions analysis.

    :param folder_filter: includes in processing only folders that contain given filter
    :param no_download: flag - do not download any statements from bank accounts
    :param no_upload: flag - do not upload anything to Buxfer
    :param updated_buxfer_password: password to be encoded (with salt) and stored in secrets.yaml
    """
    config = Configuration()
    if no_download:
        config.no_download = True
    if no_upload:
        config.no_upload = True
    if folder_filter:
        config.folder_filter = folder_filter
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
        print("\nOlder platforms may not work correctly with this code.\n"
              "The solution was developed using Python 3.9.\n"
              "Please, consider an update.\n")

    clize.run(main)
