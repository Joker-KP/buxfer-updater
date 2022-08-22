import pytest
import requests
from requests.exceptions import HTTPError

from buxfer.api import Buxfer

JSON_HEADERS = {'Content-Type': 'application/json; charset=utf-8'}
HTML_HEADERS = {'Content-Type': 'text/html; charset=UTF-8'}


def test_buxfer_alive():
    response = requests.get(f"{Buxfer.BASE_URL}/contacts")
    assert response.status_code == 400
    result = response.json()
    assert 'Access denied' in result['error']['message']


@pytest.mark.usefixtures("requests_mock")
class TestLogin:
    user = 'user'
    password = 'pass'

    def test_proper_login(self, requests_mock):
        requests_mock.post(Buxfer.LOGIN_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS,
                           json={'response': {'status': 'OK', 'token': 'SOME-TOKEN'}})
        api = Buxfer(self.user, self.password)
        assert api.token == 'SOME-TOKEN'

    def test_login_bad_status(self, requests_mock):
        requests_mock.post(Buxfer.LOGIN_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS, status_code=400,
                           json={'response': {'status': 'ERROR: wrong something'}})
        with pytest.raises(ValueError, match='ERROR: wrong something'):
            Buxfer(self.user, self.password)

    def test_login_bad_credentials(self, requests_mock):
        requests_mock.post(Buxfer.LOGIN_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS, status_code=400,
                           json={"error": {"type": "client",
                                           "message": "Email or username does not match an existing account."}},
                           )
        with pytest.raises(ValueError, match='ERROR: Email or username does not match'):
            Buxfer(self.user, self.password)

    def test_login_http_error(self, requests_mock):
        requests_mock.post(Buxfer.LOGIN_URL.format(Buxfer.BASE_URL), headers=HTML_HEADERS, status_code=404)
        with pytest.raises(HTTPError):
            Buxfer(self.user, self.password)


@pytest.mark.usefixtures("requests_mock")
class TestUploadStatement:
    @pytest.fixture()
    def buxfer_api(self, requests_mock):
        # setup
        user = 'user'
        password = 'pass'
        requests_mock.post(Buxfer.LOGIN_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS,
                           json={'response': {'status': 'OK', 'token': 'SOME-TOKEN'}})
        yield Buxfer(user, password)
        # teardown

    def test_proper_upload(self, requests_mock, buxfer_api):
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS,
                           json={'response': {'status': 'OK'}})
        result = buxfer_api.upload_statement(123, 'AAA')
        assert result is True

    def test_not_logged_in(self, requests_mock, buxfer_api):
        buxfer_api.logout()
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS,
                           json={'response': {'status': 'OK'}})
        with pytest.raises(RuntimeError, match='You must first log in properly'):
            buxfer_api.upload_statement(123, 'AAA')

    def test_bad_status(self, requests_mock, buxfer_api):
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS, status_code=400,
                           json={'response': {'status': 'ERROR: a reason'}})
        with pytest.raises(ValueError):
            buxfer_api.upload_statement(123, 'AAA')

    def test_with_error_message(self, requests_mock, buxfer_api):
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL), headers=JSON_HEADERS, status_code=400,
                           json={'error': {'message': 'some failure'}})
        with pytest.raises(ValueError):
            buxfer_api.upload_statement(123, 'AAA')

    def test_http_error(self, requests_mock, buxfer_api):
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL), headers=HTML_HEADERS, status_code=500)
        with pytest.raises(HTTPError):
            buxfer_api.upload_statement(123, 'AAA')
