import csv

import cchardet


def autodetect_encoding(file_path):
    with open(file_path, "rb") as file:
        content = file.read()
    detection = cchardet.detect(content)
    if detection['confidence'] < 0.5:
        raise ValueError("Could not detect proper encoding")
    return detection['encoding']


def load_qif(file_path):
    encoding = autodetect_encoding(file_path)
    with open(file_path, "rt", encoding=encoding) as file:
        statement_content = file.read()
    return statement_content


def is_integrity_fine(file_path, config=None, encoding=None):
    if config and 'integrity' in config:
        line_index = config['integrity']['line_index']
        line_content = config['integrity']['line_content']
        encoding = autodetect_encoding(file_path) if encoding is None else encoding
        with open(file_path, "rt", encoding=encoding) as dataset:
            lines = dataset.read().splitlines()
            actual_line = lines[line_index]
            return actual_line == line_content
    return True


def load_csv_items(file_path, row_type, encoding=None, skip_headers=0, selected_columns=None, delim=';'):
    encoding = autodetect_encoding(file_path) if encoding is None else encoding
    items = []
    with open(file_path, "rt", encoding=encoding) as dataset:
        csv_reader = csv.reader(dataset, delimiter=delim)
        for i in range(skip_headers):
            next(csv_reader)
        for row_data in csv_reader:
            if selected_columns is not None:
                selected_data = [row_data[i] for i in selected_columns]
                item = row_type(*selected_data)
            else:
                item = row_type(*row_data)
            items += [item]
    return items
