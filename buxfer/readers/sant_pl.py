import re

from buxfer.reader_base import StatementReaderBase


class SantPl(StatementReaderBase):

    def parse_amount(self, item):
        amount = self.get_attribute(item, self.config['converter']['amount_source'])
        amount = amount.replace(',', '.')  # additional comma to dot replacement (Polish locales)
        return re.sub(self.amount_accepted_pattern, '', amount)
