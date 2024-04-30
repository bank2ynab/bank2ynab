# Plugin for handling format of Handelsbanken [SE] bank export files
"""
        Strip HTML from input file, allowing it to be used by main script
        With thanks to @joacand's script from here:
        github.com/joacand/HandelsbankenYNABConverter/blob/master/Converter.py
"""

import re
import typing

from ..bank_handler import BankHandler


class Handelsbanken(BankHandler):
    def __init__(self, config_dict: dict[str, typing.Any]):
        """
        :param config_dict: a dictionary of conf parameters
        """
        super().__init__(config_dict)
        self.name = "Handelsbanken"

    def _preprocess_file(
        self, file_path: str, plugin_args: list[typing.Any]
    ) -> str:
        """
        Strips HTML from input file, modifying the input file directly
        :param file_path: path to file
        """
        with open(file_path) as input_file:
            output_rows: list[list[str]] = list()
            for row in input_file:
                cells = row.split(";")
                new_row: list[str] = list()
                for cell in cells:
                    es = re.findall(r"\\>.*?\\<", cell)
                    while "><" in es:
                        es.remove("><")
                        for n, i in enumerate(es):
                            es[n] = i[1:-1]
                    # if our cell isn't empty, add it to the row
                    if len(es) > 0:
                        new_row.append(es[0])
                # if our row isn't empty, add it to the list of rows
                if new_row:
                    output_rows.append(new_row)
        # overwrite our source file
        with open(file_path, "w") as output_file:
            for row in output_rows:
                output_file.write("{}\n".format(";".join(row)))
        return file_path


def build_bank(config: dict[str, typing.Any]) -> BankHandler:
    """This factory function is called from the main program,
    and expected to return a BankHandler subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a BankHandler subclass instance
    """
    return Handelsbanken(config)
