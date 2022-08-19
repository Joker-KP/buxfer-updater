from urllib.error import HTTPError, URLError

import requests


class Buxfer:

    BASE_URL = "https://www.buxfer.com/api"
    UPLOAD_URL = "{}/upload_statement"
    TOKEN_URL = "{}/login?userid={}&password={}"

    token = None

    @staticmethod
    def check_error(response):
        response.raise_for_status()
        result = response.json()
        if 'error' in result and 'message' in result['error']:
            raise ValueError(f"ERROR: {result['error']['message']}")
        response = result['response']
        if response['status'] != "OK":
            raise ValueError(response['status'])
        return response

    def __init__(self, user, password):
        with requests.get(self.TOKEN_URL.format(self.BASE_URL, user, password)) as response:
            response = self.check_error(response)
            self.token = response['token']

    def is_logged_in(self):
        return self.token is not None

    def upload_statement(self, account_id, statement):
        if self.token is None:
            raise RuntimeError("You must first log in properly.")

        data = {
            'token': self.token,
            'accountId': account_id,
            'statement': statement,
            'dateFormat': "DD/MM/YY",
        }
        try:
            with requests.post(self.UPLOAD_URL.format(self.BASE_URL), json=data) as response:
                response = self.check_error(response)
                return response['status'] == 'OK'
        except HTTPError as error:
            print(f'HTTP error occurred: {error.code} {error.reason}')
        except URLError as error:
            print(error.reason)
        except Exception as err:
            print(f'Other error occurred: {err}')
