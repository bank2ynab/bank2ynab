import logging

import bank_handler
from pandas import read_excel
from bank_handler import BankHandler


class XLS_Converter(BankHandler):
    def __init__(self, config_object: dict):
        """
        :param config_object: a dictionary of conf parameters
        """
        super().__init__(config_object)
        self.config = config_object

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """
        Combines all tables in a XLS file into one table and writes to CSV.

        :param file_path: path to XLS file
        :type file_path: str
        :param plugin_args: plugin arguments (unused in this plugin)
        :type plugin_args: list
        :return: path to CSV file
        :rtype: str
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
    """This factory function is called from the main program,
    and expected to return a BankHandler subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a BankHandler subclass instance
    """
    return XLS_Converter(config)
