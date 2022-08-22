import re

from buxfer.reader_base import StatementReaderBase


class CreditAgricolePl(StatementReaderBase):

    def parse_amount(self, item):
        amount = self.get_attribute(item, self.config['converter']['amount_source'])
        amount = amount.replace(',', '.')  # additional comma to dot replacement (Polish locales -> QIF)
        return re.sub(self.amount_accepted_pattern, '', amount)

    def parse_description(self, item):
        title = self.get_attribute(item, 'title')
        category = self.get_attribute(item, 'category')
        sender_no = self.get_attribute(item, 'sender_account_no')
        recipient_no = self.get_attribute(item, 'recipient_account_no')

        description = title if title else category
        if sender_no:
            description += self.get_attribute(item, '     {sender} {sender_account_no}')
        if recipient_no:
            description += self.get_attribute(item, '     {recipient} {recipient_account_no}')
        return description
