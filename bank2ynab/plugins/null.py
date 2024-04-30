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


class NullBank(BankHandler):
    """Example subclass used for testing the plugin system."""

    def __init__(self, config_dict: dict):
        """
        :param config_object: a dictionary of conf parameters
        """
        super().__init__(config_dict)
        self.name = "NullBank"

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """
        This is probably the only method you really want to override.
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - plugins can use this function
        return file_path

    def read_data(self, file_path):
        """
        Implement any custom parsing logic in here.
        :param file_path: absolute path to source file
        :return: list of lists representing rows in output format
        """
        return [
            # format of each row should be:
            # [Date,Payee,Category,Memo,Outflow,Inflow]
        ]

    def get_files(self):
        """Only override this if you need custom logic to find source
        data, e.g. downloading from somewhere.
        :return: list of absolute pathnames to source files
        """
        return []

    def write_data(self, source_file_path, data):
        """Only override this if you know read_data is not returning
        records in standard format (which you really shouldn't do anyway).
        :param source_file_path: absolute path to SOURCE file. The method will
                determine output file on its own.
        :param data: list of lists representing records
        :return: absolute path to output file
        """
        return None


def build_bank(config):
    """This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return NullBank(config)
