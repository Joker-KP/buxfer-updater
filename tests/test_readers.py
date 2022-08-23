import os

import pytest

from buxfer.loaders import autodetect_encoding
from buxfer.reader_base import StatementReaderBase
from buxfer.reader_selector import read_content, all_readers


@pytest.fixture()
def sample_path():
    base_path = os.path.dirname(__file__) + '/statements'
    return {
        'qif': f'{base_path}/qif-sample.qif',
        'nest-pl': f'{base_path}/nest-pl-sample.csv',
        'ca24-pl': f'{base_path}/ca24-pl-sample.csv'
    }


def test_autodetect_encoding_1250(sample_path):
    # NOTE. chardet made it wrong (did report Windows-1252 here); cchardet does it properly
    assert autodetect_encoding(sample_path['ca24-pl']).upper() == 'WINDOWS-1250'


def test_autodetect_encoding_utf(sample_path):
    assert autodetect_encoding(sample_path['nest-pl']).upper() == 'UTF-8'


def test_all_readers_init():
    readers = [r.__class__.__name__ for r in all_readers()]
    assert len(readers) >= 2
    assert 'NestPl' in readers
    assert 'CreditAgricolePl' in readers


@pytest.mark.parametrize('parser_id', ['qif', 'nest-pl', 'ca24-pl'])
def test_read_content(parser_id, sample_path):
    file_path = sample_path[parser_id]
    value = read_content(file_path, parser_id)
    assert '!Type:Bank' in value
    assert len(value.splitlines()) > 4


def test_base_class_should_not_instantiate():
    with pytest.raises(TypeError, match='is an abstract class'):
        StatementReaderBase('anything')
