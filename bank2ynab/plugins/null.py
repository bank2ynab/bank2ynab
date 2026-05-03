# This is a "null" plugin showing how to write your own.
# The procedure is as follows:
# 1 - Subclass B2YBank overriding the methods you need - typically just
#       read_data(path_to_file). See docstrings below for explanations.
# 2 - provide build_bank(config_dict_bool) which should return an
#       instance of your B2YBank subclass.
# 3 - save the file under the "plugins" directory, e.g. plugins/mymodule.py
# At that point, you can reference the plugin in conf files like this:
#   Plugin = mymodule

from ..bank_handler import BankHandler
from ..config_handler import BankConfig


class NullBank(BankHandler):
    """Example subclass used for testing the plugin system."""

    def __init__(self, bank_config: BankConfig) -> None:
        """Initialise NullBank handler.

        Args:
            bank_config: A BankConfig instance containing conf parameters.
        """
        super().__init__(bank_config)
        self.name = "NullBank"

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """Pre-process a file before reading (intentionally empty, override in subclasses).

        Args:
            file_path: Path to file.
            plugin_args: Plugin-specific arguments.

        Returns:
            str: Path to the (unmodified) file.
        """
        # intentionally empty - plugins can use this function
        return file_path

    def read_data(self, file_path):  # -> list[Any]:
        """Implement any custom parsing logic in here.

        Args:
            file_path: Absolute path to source file.

        Returns:
            list: List of lists representing rows in output format.
        """
        return [
            # format of each row should be:
            # [Date,Payee,Category,Memo,Outflow,Inflow]
        ]

    def get_files(self):
        """Override this for custom logic to find source data.

        Returns:
            list: List of absolute pathnames to source files.
        """
        return []

    def write_data(self, source_file_path, data) -> None:
        """Override this if read_data does not return records in standard format.

        Args:
            source_file_path: Absolute path to SOURCE file.
            data: List of lists representing records.

        Returns:
            str or None: Absolute path to output file.
        """
        return None


def build_bank(config) -> NullBank:
    """Return a NullBank instance for a given bank configuration.

    Args:
        config: A BankConfig instance containing conf parameters.

    Returns:
        NullBank: A BankHandler subclass instance.
    """
    return NullBank(config)
