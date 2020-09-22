from subprocess import Popen


def convert_file_to_format(file_to_convert:str , convert_to=None, calibre_path=None) -> str:
    if convert_to is None:
        raise ValueError('convert_to must have a value: \'pdf\', \'mobi\', \'epub\'.')

    convert_to = convert_to.lower()
    file_to_convert_filename = '.'.join(file_to_convert.split('.')[:-1])

    converted_file_filename = f'{file_to_convert_filename}.{convert_to}'

    try:
        command = f'ebook-convert {file_to_convert_filename} {converted_file_filename}'

        with open('/dev/null', 'w') as sink:
            Popen.call(command, shell=True, stdout=sink, stderr=sink)

    except Exception as err:
        raise err

    return converted_file_filename
