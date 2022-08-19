import pytest
from requests.exceptions import HTTPError

from buxfer.api import Buxfer


@pytest.mark.usefixtures("requests_mock")
class TestLogin:
    user = 'user'
    password = 'pass'

    def test_proper_login(self, requests_mock):
        requests_mock.get(Buxfer.TOKEN_URL.format(Buxfer.BASE_URL, self.user, self.password),
                          json={'response': {'status': 'OK', 'token': 'SOME-TOKEN'}})
        api = Buxfer(self.user, self.password)
        assert api.token == 'SOME-TOKEN'

    def test_login_bad_status(self, requests_mock):
        requests_mock.get(Buxfer.TOKEN_URL.format(Buxfer.BASE_URL, self.user, self.password),
                          json={'response': {'status': 'FAILED: wrong something'}})
        with pytest.raises(ValueError, match='FAILED: wrong something'):
            Buxfer(self.user, self.password)

    def test_login_with_error_message(self, requests_mock):
        requests_mock.get(Buxfer.TOKEN_URL.format(Buxfer.BASE_URL, self.user, self.password),
                          json={'error': {'message': 'some failure'}})
        with pytest.raises(ValueError, match='ERROR: some failure'):
            Buxfer(self.user, self.password)

    def test_login_http_error(self, requests_mock):
        requests_mock.get(Buxfer.TOKEN_URL.format(Buxfer.BASE_URL, self.user, self.password), status_code=404)
        with pytest.raises(HTTPError):
            Buxfer(self.user, self.password)


@pytest.mark.usefixtures("requests_mock")
class TestUploadStatement:

    @pytest.fixture()
    def buxfer_api(self, requests_mock):
        user = 'user'
        password = 'pass'
        requests_mock.get(Buxfer.TOKEN_URL.format(Buxfer.BASE_URL, user, password),
                          json={'response': {'status': 'OK', 'token': 'SOME-TOKEN'}})
        yield Buxfer(user, password)

    def test_proper_upload(self, requests_mock, buxfer_api):
        requests_mock.post(Buxfer.UPLOAD_URL.format(Buxfer.BASE_URL),
                           json={'response': {'status': 'OK'}})
        result = buxfer_api.upload_statement(123, 'AAA')
        assert result is True
