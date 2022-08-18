import sys


def filter_content(filename, statement_content, extension_filter):
    if extension_filter == "qif":
        if not filename.endswith("qif"):
            extension = filename[-len(extension_filter):]
            print(f"Warning: incoherent statement file extension ({extension} vs {extension_filter})")
        return statement_content

    # TODO: filtering / processing other then *.qif

    print(f"Error: Unknown filter used: {extension_filter}")
    sys.exit(2)
