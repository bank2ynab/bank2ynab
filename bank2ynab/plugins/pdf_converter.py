import tabula
from bank_process import B2YBank


class PDF_Converter(B2YBank):
    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(PDF_Converter, self).__init__(config_object)
        self.name = "PDF_Converted_Bank"

    def _preprocess_file(self, file_path):
        dfs = tabula.read_pdf(file_path, pages="all")

        return dfs[2]


def build_bank(config):
    """This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return PDF_Converter(config)
