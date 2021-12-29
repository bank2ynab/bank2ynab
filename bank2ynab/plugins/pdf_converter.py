import os

import tabula
from bank_handler import BankHandler


class PDF_Converter(BankHandler):
    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(PDF_Converter, self).__init__(config_object)
        self.config = config_object

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """dfs = tabula.read_pdf(
            file_path,
            pages="all",
            output_format="dataframe",
            multiple_tables=True,
        )"""
        # chosen_df = int(plugin_args[0])
        new_path = get_output_path(file_path, self.config["bank_name"])
        """ dfs[chosen_df].to_csv(
            new_path,
            index=False,
            encoding="utf-8",
        ) """
        tabula.convert_into(
            file_path,
            new_path,
            output_format="csv",
            pages="all",
        )

        return new_path


def get_output_path(original_path: str, bank_name: str) -> str:
    target_dir = os.path.dirname(original_path)
    new_filename = f"converted pdf statement - {bank_name}.csv"
    while os.path.isfile(new_filename):
        counter = 1
        new_filename = f"converted pdf statement - {bank_name}_{counter}.csv"
        counter += 1
    return os.path.join(target_dir, new_filename)


def build_bank(config):
    """This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return PDF_Converter(config)
