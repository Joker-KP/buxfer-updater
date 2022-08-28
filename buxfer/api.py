import logging

import requests


class Buxfer:
    BASE_URL = "https://www.buxfer.com/api"
    UPLOAD_URL = "{}/upload_statement"
    LOGIN_URL = "{}/login"

    token = None

    @staticmethod
    def check_error(response):
        content_type = response.headers.get('content-type')
        if 'json' not in content_type:
            response.raise_for_status()
        result = response.json()
        if 'error' in result and 'message' in result['error']:
            raise ValueError(f"ERROR: {result['error']['message']}")
        response_text = result['response']
        if response_text['status'] != "OK":
            raise ValueError(response_text['status'])
        response.raise_for_status()
        return response_text

    def __init__(self, user, password):
        data = {
            'userid': user,
            'password': password
        }
        logging.debug(f'Buxfer log in for user {data["userid"]}')
        with requests.post(self.LOGIN_URL.format(self.BASE_URL), json=data) as response:
            response = self.check_error(response)
            self.token = response['token']
            logging.debug(f'Token received: {self.token[0:8]}...')

    def is_logged_in(self):
        return self.token is not None

    def logout(self):
        self.token = None

    def upload_statement(self, account_id, statement):
        if self.token is None:
            raise RuntimeError("You must first log in properly.")

        data = {
            'token': self.token,
            'accountId': account_id,
            'statement': statement,
            'dateFormat': "DD/MM/YY",
        }
        partial_statement = data["statement"][0:30].replace('\n', '^')
        logging.debug(f'Buxfer upload to account {data["accountId"]} statement: "{partial_statement}..."')
        with requests.post(self.UPLOAD_URL.format(self.BASE_URL), json=data) as response:
            response = self.check_error(response)
            return response['status'] == 'OK'
