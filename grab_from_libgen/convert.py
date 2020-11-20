import os
from subprocess import Popen


class CalibreError(Exception):
    pass


class ConversionError(Exception):
    pass


def convert_file_to_format(file_to_convert: str, convert_to: str) -> str:
    if convert_to.lower() not in {'pdf', 'mobi', 'epub'}:
        raise ConversionError('convert_to must have a value: \'pdf\', \'mobi\', \'epub\'.')

    convert_to = convert_to.lower()
    file_to_convert_filename = '.'.join(file_to_convert.split('.')[:-1])

    converted_file_filename = f'{file_to_convert_filename}.{convert_to}'

    command = ['ebook-convert', file_to_convert, converted_file_filename]

    with open('/dev/null', 'w') as sink:
        proc = Popen(command)
        proc.wait()

    return converted_file_filename
