import os

import pytest

from buxfer.loaders import autodetect_encoding
from buxfer.reader_base import StatementReaderBase
from buxfer.reader_selector import read_content, all_readers

nest_path = os.path.dirname(__file__) + '/statements/nest-sample.csv'
ca24_path = os.path.dirname(__file__) + '/statements/ca24-sample.csv'


def test_autodetect_encoding_1250():
    # NOTE. chardet made it wrong (did report Windows-1252 here); cchardet does it properly
    assert autodetect_encoding(ca24_path).upper() == "Windows-1250".upper()


def test_autodetect_encoding_utf():
    assert autodetect_encoding(nest_path).upper() == "UTF-8".upper()


def test_all_readers():
    readers = [r.__class__.__name__ for r in all_readers()]
    assert len(readers) >= 2
    assert 'NestPl' in readers
    assert 'CreditAgricolePl' in readers


def test_read_content_nest():
    value = read_content(nest_path, 'nest')
    assert '!Type:Bank' in value
    assert len(value.splitlines()) > 4


def test_read_content_ca24():
    value = read_content(ca24_path, 'ca24')
    assert '!Type:Bank' in value
    assert len(value.splitlines()) > 4


def test_base_class_should_not_instantiate():
    with pytest.raises(TypeError, match='is an abstract class'):
        StatementReaderBase("anything")
