import csv
import re
from datetime import datetime
from typing import NamedTuple

import cchardet


def filter_content(filename, extension_filter):
    if extension_filter == "qif":
        if not filename.endswith("qif"):
            extension = filename[-len(extension_filter):]
            print(f"Warning: incoherent statement file extension ({extension} vs {extension_filter})")
        return read_qif(filename)
    elif extension_filter == "ca24":
        if not filename.endswith("csv"):
            extension = filename[-len(extension_filter):]
            print(f"Warning: incoherent statement file extension ({extension} vs csv)")
        return convert_from_credit_agricole_csv(filename)

    raise RuntimeError(f"Error: Unknown filter used: {extension_filter}")


class CreditAgricoleTrans(NamedTuple):
    # --- indices 0 - 18
    account_from: str  # From account
    category: str  # Transaction category
    created_in: str  # Commissioned in
    transaction_type: str  # Transaction type
    account_no: str  # Account number
    sender: str  # Sender
    sender_address: str  # Address
    sender_country: str  # Country
    sender_account_no: str  # Sender account
    sender_short_no: str  # Short account number
    recipient: str  # Recipient
    recipient_bic: str  # Recipient's bank BIC (SWIFT code)
    recipient_bank_name: str  # Recipient's bank name
    recipient_address: str  # Address
    recipient_country: str  # Country
    recipient_account_no: str  # Recipient account
    recipient_short_no: str  # Short account number
    title: str  # Title
    payer: str  # Payer
    # --- indices 68 - 70
    operation: str  # Operation
    operation_date: str  # Operation date
    operation_book_date: str  # Book date
    # --- indices 81 - 88
    amount: str  # Amount
    commission: str  # Commission
    commission_account: str  # Commission account
    balance: str  # Balance after transaction
    description: str  # Description
    service: str  # Representative service
    transfer_id: str  # Express transfer ID
    blik_id: str  # BLIK transfer ID


def convert_credit_agricole_item(item: CreditAgricoleTrans):
    input_format = "%d.%m.%Y"
    output_format = "%d/%m/%y"
    date = datetime.strptime(item.operation_date, input_format).strftime(output_format)

    amount = item.amount.replace(',', '.')
    amount = re.sub('[^-0-9\.]', '', amount)

    spaces = "     "
    desc = item.title if len(item.title) > 0 else item.category
    if len(item.sender_account_no) > 0:
        desc += f"{spaces}{item.sender} {item.sender_account_no}"
    if len(item.recipient_account_no) > 0:
        desc += f"{spaces}{item.recipient} {item.recipient_account_no}"

    return f"D{date}\nP{desc}\nT{amount}\nC*\n^\n"


def read_qif(filename):
    encoding = autodetect_encoding(filename)
    with open(filename, "rt", encoding=encoding) as file:
        statement_content = file.read()
    return statement_content


def convert_from_credit_agricole_csv(filename):
    selected_columns = [*range(0, 19), *range(68, 71), *range(81, 89)]
    items = transactions_from_csv(filename, CreditAgricoleTrans, skip_headers=1, selected_columns=selected_columns)
    result = "!Type:Bank\n"
    for item in items:
        result += convert_credit_agricole_item(item)
    return result


def autodetect_encoding(filename):
    with open(filename, "rb") as file:
        content = file.read()
    detection = cchardet.detect(content)
    if detection['confidence'] < 0.5:
        raise ValueError("Could not detect proper encoding")
    return detection['encoding']


def transactions_from_csv(csv_path, row_type, encoding=None, skip_headers=0, selected_columns=None, delim=';'):
    encoding = autodetect_encoding(csv_path) if encoding is None else encoding
    transactions = []
    with open(csv_path, "rt", encoding=encoding) as datasets:
        csv_reader = csv.reader(datasets, delimiter=delim)
        for i in range(skip_headers):
            next(csv_reader)
        for row_data in csv_reader:
            if selected_columns is not None:
                selected_data = [row_data[i] for i in selected_columns]
                transaction = row_type(*selected_data)
            else:
                transaction = row_type(*row_data)
            transactions += [transaction]
    return transactions
