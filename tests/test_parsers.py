import os

import pytest

from buxfer.readers.ca24_pl import CreditAgricolePl
from buxfer.readers.nest_pl import NestPl

nest_path = os.path.dirname(__file__) + '/statements/nest-sample.csv'
ca24_path = os.path.dirname(__file__) + '/statements/ca24-sample.csv'


class TestNestStatementReader:
    @pytest.fixture()
    def reader_nest(self):
        return NestPl(None)

    @pytest.fixture()
    def item_nest(self, reader_nest):
        return reader_nest.item_type(
            *['27-08-2021', '25-08-2021', 'Transfer', '-2 117.89', 'PLN', 'John Doe',
              '11223344', 'my own title', '20.00'])

    def test_id(self, reader_nest):
        value = reader_nest.identifier()
        assert value == 'nest'

    def test_extension(self, reader_nest):
        value = reader_nest.expected_input_extension()
        assert value == '.csv'

    def test_parse_date(self, reader_nest, item_nest):
        value = reader_nest.parse_date(item_nest)
        assert value == '25/08/21'

    def test_parse_amount(self, reader_nest, item_nest):
        value = reader_nest.parse_amount(item_nest)
        assert value == '-2117.89'

    def test_parse_description(self, reader_nest, item_nest):
        value = reader_nest.parse_description(item_nest)
        assert value == 'my own title     John Doe 11223344'

    def test_convert(self, reader_nest, item_nest):
        value = reader_nest.convert(item_nest)
        assert value == 'D25/08/21\nPmy own title     John Doe 11223344\nT-2117.89\nC*\n^\n'

    def test_process(self, reader_nest):
        value = reader_nest.process_file(nest_path)
        assert reader_nest.qif_header in value
        assert len(value.splitlines()) > 4


class TestCreditAgricoleStatementReader:
    @pytest.fixture()
    def reader_ca(self):
        return CreditAgricolePl(None)

    @pytest.fixture()
    def item_ca(self, reader_ca):
        return reader_ca.item_type(
            *['Transfer', 'Mr Pan', '00 3400 1234', 'John Doe', '123 000 333', 'my own title',
              '25.08.2021 14:34:57', '-2 117.89 PLN'])

    def test_id(self, reader_ca):
        value = reader_ca.identifier()
        assert value == 'ca24'

    def test_extension(self, reader_ca):
        value = reader_ca.expected_input_extension()
        assert value == '.csv'

    def test_parse_date(self, reader_ca, item_ca):
        value = reader_ca.parse_date(item_ca)
        assert value == '25/08/21'

    def test_parse_amount(self, reader_ca, item_ca):
        value = reader_ca.parse_amount(item_ca)
        assert value == '-2117.89'

    def test_parse_description(self, reader_ca, item_ca):
        value = reader_ca.parse_description(item_ca)
        assert value == 'my own title     Mr Pan 00 3400 1234     John Doe 123 000 333'

    def test_convert(self, reader_ca, item_ca):
        value = reader_ca.convert(item_ca)
        assert value == 'D25/08/21\nPmy own title     Mr Pan 00 3400 1234     John Doe 123 000 333\nT-2117.89\nC*\n^\n'

    def test_process(self, reader_ca):
        value = reader_ca.process_file(ca24_path)
        assert reader_ca.qif_header in value
        assert len(value.splitlines()) > 4
