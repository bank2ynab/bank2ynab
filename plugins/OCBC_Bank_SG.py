# Plugin for handling OCBC Bank [SG] files

from bank2ynab import B2YBank


class OCBC_Bank_SG(B2YBank):
    """ Example subclass used for testing the plugin system."""

    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(OCBC_Bank_SG, self).__init__(config_object)
        self.name = "OCBC_Bank_SG"

    def _preprocess_file(self, file_path):
        """
        For every row that doesn't have a valid date field
        strip out separators and append to preceding row.
        Overwrite input file with modified output.
        :param file_path: path to file
        """
        # what do we actually want to do?
        header_rows = int(self.config["header_rows"])
        footer_rows = int(self.config["footer_rows"])

        # get total number of rows in transaction file using a generator
        with open(file_path) as row_counter:
            row_count = sum(1 for _ in row_counter)

        with open(file_path) as input_file:
            output_rows = []
            for rownum, row in enumerate(input_file):
                # append headers and footers without modification
                if rownum < header_rows or rownum > (row_count - footer_rows):
                    output_rows.append(row)
                    continue
                if row[0] == ",":
                    # join with the previous row but excluding the newline char
                    # of the previous row
                    output_rows[-1] = (
                        output_rows[-1][:-1] + "," + row.strip(" ,")
                    )
                else:
                    output_rows.append(row)

        # overwrite source file
        with open(file_path, "w") as output_file:
            for row in output_rows:
                output_file.write(row)
        return


def build_bank(config):
    """ This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return OCBC_Bank_SG(config)
