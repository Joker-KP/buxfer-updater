import inspect
import re
from collections import namedtuple
from datetime import datetime

import yaml

from buxfer.loaders import load_csv_items


class StatementReaderBase:
    """
    Base class for statement parsers. Each child class is reassured to be a singleton,
    and responsible to convert transactions list from a specific bank (assumed as CSV file)
    to the format that is understandable for the Buxfer API (QIF format as default).
    May implement any conversion overriding:
    - parse_[field] - to only change the way specific field is prepared
    - convert - to control the whole transaction (single CSV row) conversion
    - process_file - to gain full control over the output format
    Most cases should be covert by creating only configuration file (single yaml for a CSV file from a specific bank)
    """
    _instances = {}

    # inter-classes defaults
    amount_accepted_pattern = r'[^-0-9\.]'  # digits, minus and dot
    field_name_pattern = r'{([0-9a-zA-Z_]+)}'
    date_output_format = '%d/%m/%y'
    qif_header = '!Type:Bank\n'
    qif_item_pattern = 'D{date}\nP{description}\nT{amount}\nC*\n^\n'

    def __new__(cls, config_path):
        if cls is StatementReaderBase:
            raise TypeError(f'{cls.__name__} is an abstract class')
        elif cls not in StatementReaderBase._instances:
            StatementReaderBase._instances[cls] = super().__new__(cls)
            StatementReaderBase._instances[cls]._init(config_path)
        return StatementReaderBase._instances[cls]

    # initialization moved from __init__ method here
    # to prevent subsequent "creations" to change the initial values of the <singleton children>
    def _init(self, config_path=None):
        if not config_path:
            config_path = inspect.getfile(self.__class__).replace(".py", ".yaml")
        self.selected_idx = []  # idx of columns in CSV
        self.selected_names = []
        with open(config_path, 'r') as file:
            self.config = yaml.full_load(file)
        for field in self.config['fields']:
            self.selected_idx += [field[0]]
            self.selected_names += [field[1]]
        self.item_type = namedtuple(self.identifier() + '_tuple', self.selected_names)

    def identifier(self):
        return self.config['identifier']

    def expected_input_extension(self):
        return self.config['input_extension']

    def get_attribute(self, item, name_pattern_or_index):
        if isinstance(name_pattern_or_index, str):
            if '{' not in name_pattern_or_index:
                return getattr(item, name_pattern_or_index)  # direct field name
            format_string = re.sub(self.field_name_pattern, '{}', name_pattern_or_index)
            field_names = re.findall(self.field_name_pattern, name_pattern_or_index)
            fields = [self.get_attribute(item, i) for i in field_names]
            return format_string.format(*fields)
        if isinstance(name_pattern_or_index, int):
            index = self.selected_idx.index(name_pattern_or_index)
            return item[index]
        raise ValueError('Source should contain field name(s) or single index')

    def parse_date(self, item):
        input_format = self.config['converter']['date_input_format']
        input_date = self.get_attribute(item, self.config['converter']['date_source'])
        return datetime.strptime(input_date, input_format).strftime(self.date_output_format)

    def parse_amount(self, item):
        input_amount = self.get_attribute(item, self.config['converter']['amount_source'])
        return re.sub(self.amount_accepted_pattern, '', input_amount)

    def parse_description(self, item):
        return self.get_attribute(item, self.config['converter']['description_source'])

    def convert(self, item):
        date = self.parse_date(item)
        amount = self.parse_amount(item)
        desc = self.parse_description(item)
        return self.qif_item_pattern.format(date=date, description=desc, amount=amount)

    def process_file(self, statement_file_path):
        items = load_csv_items(statement_file_path, self.item_type, skip_headers=self.config['skip_headers'],
                               delim=self.config['delimiter'], selected_columns=self.selected_idx)
        result = self.qif_header
        for item in items:
            result += self.convert(item)
        return result
