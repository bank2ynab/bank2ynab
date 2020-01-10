# Step 1: See https://github.com/bank2ynab/bank2ynab/wiki/WorkingWithPlugins
# Step 2: Copy this template into a new file.
# Step 3: Replace "YourActualBank" below with a descriptive bank name

from bank2ynab import B2YBank


class YourActualBankPlugin(B2YBank):
    def __init__(self, config_object):
        super(YourActualBankPlugin, self).__init__(config_object)
        self.name = "YourActualBank"

    def _preprocess_file(self, file_path):
        """
        This is an example of how to preprocess the transaction file
        prior to feeding the data into the main read_data function.
        Any specialised string or format operations can easily
        be done here.
        """
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
    return YourActualBankPlugin(config)
