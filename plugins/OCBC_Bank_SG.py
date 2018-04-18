# Plugin for handling OCBC Bank [SG] files

from bank2ynab import B2YBank


class NullBank(B2YBank):
    """ Example subclass used for testing the plugin system."""
    def __init__(self, config_object, is_py2):
        """
        :param config_object: a dictionary of conf parameters
        :param is_py2: boolean indicating if we're running under
                        Python 2.x
        """
        super(NullBank, self).__init__(config_object, is_py2)
        self.name = "NullBank"

    def _preprocess_file(self, file_path):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # what do we actually want to do?
        return


def build_bank(config, is_py2):
    """ This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :param is_py2: boolean indicating whether we are running under Python 2.x
    :return: a B2YBank subclass instance
    """
    return NullBank(config, is_py2)
