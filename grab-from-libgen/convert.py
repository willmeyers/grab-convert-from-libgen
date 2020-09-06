from subprocess import Popen


def convert_file_to_format(file_to_convert, convert_to=None, calibre_path=None):
    if convert_to is None:
        raise ValueError('convert_to must have a value: \'pdf\', \'mobi\', \'epub\'.')

    convert_to = convert_to.lower()
    file_to_convert_filename = '.'.join(file_to_convert.split('.')[:-1])

    converted_file_to_convert_filename = f'{file_to_convert_filename}.{convert_to}'
