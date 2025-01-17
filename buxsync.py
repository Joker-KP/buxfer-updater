import hashlib
import logging
import os
import re
import sys
import time

import clize

from buxfer.api import Buxfer
from buxfer.reader_selector import read_content
from config import Configuration, buxfer_auth_data, update_secrets
from history import History
from uivision.launcher import download_statement

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


def setup_logging(log_level=logging.INFO):
    logging.basicConfig(
        level=log_level,
        filename='buxsync.log',
        format='%(asctime)s [%(levelname)s] %(message)s',
    )
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter('[%(levelname)7s] %(message)s'))
    logging.getLogger('').addHandler(console)


def md5(file_path: str):
    with open(file_path, "rb") as file:
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_account_folders(account_data_dir: str, folder_filter=''):
    """
    Look for folders which define bank accounts to process. The pattern for sub-folder is
    "Name [BUXFER_ID;PARSER_ID]"
    Name is just for easier user reference to these folders. BUXFER_ID is the account id to which you
    want to upload the statement in your buxfer.com account (click on account in Buxfer and check browser URI
    - https://www.buxfer.com/account?id=XXX - the XXX part is your id). PARSER_ID defines the way the
    statement should be preprocessed before sending to buxfer. 'qif' is the default format (it just reads
    *.qif file and send it further to Buxfer). There are also exemplary implementation for Nest Bank PL ('nest')
    and Credit Agricole PL ('ca24'). See buxfer/readers folder for details.

    :param account_data_dir: directory path where sub-folders are supposed to define bank accounts/scenarios
    :param folder_filter: will include only those sub-folders which name includes given filter
    """
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
    history = History(f'{config.account_data_dir}/history.yaml')
    folders = get_account_folders(config.account_data_dir, config.folder_filter)
    for folder in folders:
        account_id = folder['account_id']
        parser_identifier = folder['reader_id']
        logging.info(f"- Folder check: {folder['name']} (id: {account_id}, format: {parser_identifier})")
        history.log_start(account_id, folder['name'], parser_identifier)

        # download new statement from online bank
        account_folder = f"{config.account_data_dir}/{folder['entry']}"
        if not config.no_download:
            try:
                status, msg, basename = download_statement(account_folder, account_id, config)
                history.log_download_result(account_id, status, msg, basename)
            except Exception as e:
                logging.error("Exception occurred while statement download", exc_info=True)
                history.log_download_result(account_id, False, str(e), None)

        # keep existing hashes
        md5file = f"{account_folder}/md5s.txt"
        md5content = ""
        if os.path.exists(md5file):
            with open(md5file, "r") as file:
                md5content = file.read()
        md5orig = md5content

        # if not done before: convert the statement, upload to Buxfer and keep the hash
        for entry in os.listdir(f"{account_folder}"):
            statement_file = f"{account_folder}/{entry}"
            if os.path.isfile(statement_file) and entry != "md5s.txt":
                md5hash = md5(statement_file)
                if md5hash not in md5content:
                    try:
                        statement_content = read_content(statement_file, parser_identifier)
                        if not config.no_upload:
                            logging.info(f"-- Uploading {entry}...")
                            if buxfer_api.upload_statement(account_id, statement_content):
                                # // if ok -> keep md5 (no further uploads of this file)
                                logging.info("-- Upload OK")
                                md5content += f"{md5hash}\n"
                                history.log_upload_result(account_id, True, "OK", entry)
                            else:
                                history.log_upload_result(account_id, False, "Bad status", entry)
                    except Exception as e:
                        logging.error("Exception occurred while processing for upload", exc_info=True)
                        history.log_upload_result(account_id, False, str(e), entry)

        if md5orig != md5content:
            with open(md5file, "w") as file:
                file.write(md5content)

        # additional time for sync
        time.sleep(2)


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
    setup_logging(LOG_LEVELS[config.log_level])
    if no_download:
        config.no_download = True
    if no_upload:
        config.no_upload = True
    if folder_filter:
        config.folder_filter = folder_filter
    if updated_buxfer_password:
        update_secrets(updated_buxfer_password, config.salt)
        return

    logging.info(f'Started... (log level: {config.log_level})')
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
