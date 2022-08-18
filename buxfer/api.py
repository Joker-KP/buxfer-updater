import sys
from urllib.error import HTTPError, URLError

import requests

base = "https://www.buxfer.com/api"
upload_url = "{}/upload_statement"
token_url = "{}/login?userid={}&password={}"


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
