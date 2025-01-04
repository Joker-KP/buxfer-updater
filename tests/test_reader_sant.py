import pytest

from buxfer.readers.sant_pl import SantPl
# noinspection PyUnresolvedReferences
from tests.test_readers import sample_path


class TestSantStatementReader:
    @pytest.fixture()
    def reader(self):
        return SantPl(None)

    @pytest.fixture()
    def item(self, reader):
        return reader.item_type(
            *['27-08-2021', '25-08-2021', 'my own title', 'John Doe', '11223344',
              '-2117,89', '20,10', '123'])

    def test_id(self, reader):
        value = reader.identifier()
        assert value == 'sant-pl'

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
        assert value == 'my own title     John Doe 11223344'

    def test_convert(self, reader, item):
        value = reader.convert(item)
        assert value == 'D25/08/21\nPmy own title     John Doe 11223344\nT-2117.89\nC*\n^\n'

    @pytest.mark.usefixtures("sample_path")
    def test_process(self, reader, sample_path):
        value = reader.process_file(sample_path['sant-pl'])
        assert reader.qif_header in value
        assert len(value.splitlines()) > 4
