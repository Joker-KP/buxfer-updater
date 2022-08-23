import pytest

from buxfer.readers.ca24_pl import CreditAgricolePl
# noinspection PyUnresolvedReferences
from tests.test_readers import sample_path


class TestCreditAgricoleStatementReader:
    @pytest.fixture()
    def reader(self):
        return CreditAgricolePl(None)

    @pytest.fixture()
    def item(self, reader):
        return reader.item_type(
            *['Transfer', 'Mr Pan', '00 3400 1234', 'John Doe', '123 000 333', 'my own title',
              '25.08.2021 14:34:57', '-2 117.89 PLN'])

    def test_id(self, reader):
        value = reader.identifier()
        assert value == 'ca24'

    def test_extension(self, reader):
        value = reader.expected_input_extension()
        assert value == '.csv'

    def test_parse_date(self, reader, item):
        value = reader.parse_date(item)
        assert value == '25/08/21'

    def test_parse_amount(self, reader, item):
        value = reader.parse_amount(item)
        assert value == '-2117.89'

    def test_parse_description(self, reader, item):
        value = reader.parse_description(item)
        assert value == 'my own title     Mr Pan 00 3400 1234     John Doe 123 000 333'

    def test_convert(self, reader, item):
        value = reader.convert(item)
        assert value == 'D25/08/21\nPmy own title     Mr Pan 00 3400 1234     John Doe 123 000 333\nT-2117.89\nC*\n^\n'

    @pytest.mark.usefixtures("sample_path")
    def test_process(self, reader, sample_path):
        value = reader.process_file(sample_path['ca24'])
        assert reader.qif_header in value
        assert len(value.splitlines()) > 4
