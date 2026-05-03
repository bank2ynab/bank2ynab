import logging

from pandas import read_excel

from .. import bank_handler
from ..bank_handler import BankHandler


class XLS_Converter(BankHandler):
    def __init__(self, config_object: dict):
        """Initialise XLS converter with bank configuration.

        Args:
            config_object: A dictionary of conf parameters.
        """
        super().__init__(config_object)
        self.config = config_object

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """Combine all tables in an XLS file into one table and write to CSV.

        Args:
            file_path: Path to XLS file.
            plugin_args: Plugin arguments (unused in this plugin).

        Returns:
            str: Path to CSV file.
        """
        logging.info("Converting XLS file...")

        # create dataframe from xls
        df = read_excel(file_path)
        # generate output path
        new_path = bank_handler.get_output_path(
            input_path=file_path,
            prefix=f"Converted XLS_{self.config['bank_name']}_",
            ext=".csv",
        )
        # write the dataframe to output file
        df.to_csv(new_path, index=False)
        logging.info("\tFinished converting XLS file.")
        return new_path


def build_bank(config):
    """Return an XLS_Converter instance for a given bank configuration.

    Args:
        config: Dict containing all available configuration parameters.

    Returns:
        XLS_Converter: A BankHandler subclass instance.
    """
    return XLS_Converter(config)
