# Plugin for handling format of Handelsbanken [SE] bank export files
"""Strip HTML from input file, allowing it to be used by the main script.

With thanks to @joacand's script:
github.com/joacand/HandelsbankenYNABConverter/blob/master/Converter.py
"""

import re
import typing

from ..bank_handler import BankHandler
from ..config_handler import BankConfig


class Handelsbanken(BankHandler):
    def __init__(self, bank_config: BankConfig) -> None:
        """Initialise Handelsbanken bank handler.

        Args:
            bank_config: A BankConfig instance containing conf parameters.
        """
        super().__init__(bank_config)
        self.name = "Handelsbanken"

    def _preprocess_file(self, file_path: str, plugin_args: list[typing.Any]) -> str:
        """Strip HTML from input file, modifying the input file directly.

        Args:
            file_path: Path to file.
            plugin_args: Plugin-specific arguments (unused).

        Returns:
            str: Path to the modified file.
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


def build_bank(config: BankConfig) -> BankHandler:
    """Return a Handelsbanken instance for a given bank configuration.

    Args:
        config: Dict containing all available configuration parameters.

    Returns:
        Handelsbanken: A BankHandler subclass instance.
    """
    return Handelsbanken(config)
