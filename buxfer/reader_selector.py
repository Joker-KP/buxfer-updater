import importlib
import inspect
import os
import pkgutil

from buxfer.loaders import load_qif
from buxfer.reader_base import StatementReaderBase


def all_readers():
    subfolder = "readers"
    readers = []
    # import all modules in folder with readers
    pkg_dir = os.path.dirname(__file__) + f'/{subfolder}'
    for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
        importlib.import_module(f'.{subfolder}.' + name, __package__)
    # after the import subclasses collection is available
    for subclass in StatementReaderBase.__subclasses__():
        config_path = inspect.getfile(subclass).replace(".py", ".yaml")
        readers += [subclass(config_path)]
    return readers


def read_content(file_path, parser_identifier):
    msg = "Warning: incoherent statement file extension (file '{file}' expected to be '*{ext}')"

    if parser_identifier == "qif":
        expected_extension = ".qif"
        if not file_path.endswith(expected_extension):
            basename = os.path.basename(file_path)
            print(msg.format(file=basename, ext=expected_extension))
        return load_qif(file_path)

    for reader in all_readers():
        if reader.identifier() == parser_identifier:
            expected_extension = reader.expected_input_extension()
            if not file_path.endswith(expected_extension):
                basename = os.path.basename(file_path)
                print(msg.format(file=basename, ext=expected_extension))
            return reader.process_file(file_path)

    raise RuntimeError(f"Error: Unknown parser id used: {parser_identifier}")
