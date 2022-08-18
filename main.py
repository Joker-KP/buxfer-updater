import datetime
import hashlib
import os
import re
import sys
from urllib.error import HTTPError, URLError

import cryptocode
import requests

from defaults.settings import get_ff_binary, get_ff_download_dir
from uivision.launcher import play_and_wait

ff_bin = get_ff_binary()
ff_download_dir = get_ff_download_dir()
ui_vision_init = os.path.abspath('uivision/ui.vision.html')
ui_vision_file_storage = True
default_timeout = 140

base = "https://www.buxfer.com/api"
upload_url = "{}/upload_statement"
token_url = "{}/login?userid={}&password={}"
data_dir = 'data'

salt = os.getcwd()


def get_account_folders():
    result = []
    pattern = r'([^\[]+)\[([\d]+);([^\]]+)]'
    for entry in os.listdir(data_dir):
        if os.path.isdir(data_dir + '/' + entry):
            matches = re.match(pattern, entry)
            if matches:
                result += [{'entry': entry,
                            'name': matches[1],
                            'account_id': matches[2],
                            'filter': matches[3]}]
    return result


def filter_content(filename, statement_content, extension_filter):
    if extension_filter == "qif":
        if not filename.endswith("qif"):
            extension = filename[-len(extension_filter):]
            print(f"Warning: incoherent statement file extension ({extension} vs {extension_filter})")
        return statement_content

    # TODO: filtering / processing other then *.qif

    print(f"Error: Unknown filter used: {extension_filter}")
    sys.exit(2)


def md5(path):
    with open(path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def download_statement(account_folder, account_id):
    ui_result = play_and_wait(f'accounts/{account_id}', timeout_seconds=default_timeout,
                              use_file_storage=ui_vision_file_storage,
                              path_download_dir=ff_download_dir,
                              path_autorun_html=ui_vision_init,
                              browser_path=ff_bin)
    if 'file' not in ui_result:
        print("Problem with UI.Vision result:", ui_result['status'])
        return

    # move to the right place for upload
    downloaded = ui_result['file']
    basename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '__' + os.path.basename(downloaded)
    target = os.path.join(account_folder, basename)
    os.rename(downloaded, target)


def folders_walk(token):
    folders = get_account_folders()
    for folder in folders:
        account_id = folder['account_id']
        extension_filter = folder['filter']
        print(f"Folder check: {folder['name']} (id: {account_id}, format: {extension_filter})")

        account_folder = f"{data_dir}/{folder['entry']}"
        download_statement(account_folder, account_id)

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
                    with open(statement_file, "r") as file:
                        statement_content = file.read()
                    statement_content = filter_content(entry, statement_content, extension_filter)
                    if upload_statement(token, account_id, statement_content):
                        # // if ok -> keep md5 (no further uploads of this file)
                        print("OK")
                        md5content += f"{md5hash}\n"

        if md5orig != md5content:
            with open(md5file, "w") as file:
                file.write(md5content)


def check_error(response):
    result = response.json()
    if 'error' in result and 'message' in result['error']:
        print(f"ERROR: {result['error']['message']}")
        sys.exit(1)
    response = result['response']
    if response['status'] != "OK":
        print("An error occurred: %s" % response['status'].replace('ERROR: ', ''))
        sys.exit(1)
    return response


def get_token(user, password):
    try:
        with requests.get(token_url.format(base, user, password)) as response:
            response = check_error(response)
            return response['token']
    except HTTPError as error:
        print(f'HTTP error occurred: {error.code} {error.reason}')
    except URLError as error:
        print(error.reason)
    except Exception as err:
        print(f'Other error occurred: {err}')


def upload_statement(token, account_id, statement):
    data = {
        'token': token,
        'accountId': account_id,
        'statement': statement,
        'dateFormat': "DD/MM/YY",
    }
    try:
        with requests.post(upload_url.format(base), json=data) as response:
            response = check_error(response)
            return response['status'] == 'OK'
    except HTTPError as error:
        print(f'HTTP error occurred: {error.code} {error.reason}')
    except URLError as error:
        print(error.reason)
    except Exception as err:
        print(f'Other error occurred: {err}')


def make_ciphered_txt(txt):
    encoded = cryptocode.encrypt(txt, salt)
    print(encoded)
    sys.exit(0)


def get_auth_data():
    with open("secrets.txt", "r") as f:
        content = f.read().splitlines()
    if len(content) < 2:
        print("Missing username and/or password in secrets.txt")
    return content[0], cryptocode.decrypt(content[1], salt)


def main():
    # make_ciphered_txt('some_pass')
    print(f'Started...')
    username, password = get_auth_data()
    token = get_token(username, password)
    if token is not None:
        folders_walk(token)


if __name__ == '__main__':
    main()

    # r = play_and_wait('Accounts/1373670', timeout_seconds=default_timeout,
    #                    path_download_dir=ff_download_dir,
    #                    path_autorun_html=ui_vision_init,
    #                    browser_path=ff_bin)
    #
    # print(r)
    # if 'file' in r:
    #      print("DOWNLOAD FINE")
