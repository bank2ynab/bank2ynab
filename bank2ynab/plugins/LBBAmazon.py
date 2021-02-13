# Plugin for handling [DE LBB Amazon] format
# This handles the issue that the format has outflows that are negative
# (indicating an actual inflow) which is a combination
# that bank2ynab does not handle. This could also be handled in the
# bank2ynab code itself (-outflow --> inflow)
from bank_process import B2YBank

class LBBAmazonPlugin(B2YBank):
    def __init__(self, config_object):
        super(LBBAmazonPlugin, self).__init__(config_object)
        self.name = "LBBAmazon"

    def _preprocess_file(self, file_path):
        header_rows = int(self.config["header_rows"])
        footer_rows = int(self.config["footer_rows"])
        delimiter = self.config["input_delimiter"]

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

                split = row.split(delimiter)
                outflow = split[8]
                # Note: The format has quotation marks around values
                if outflow.startswith("\"-"):
                    # This is actually an inflow, exchange the sign
                    split[8] = "\"+{}".format(outflow[2:])
                new_row = delimiter.join(split)
                output_rows.append(new_row)

        # overwrite source file
        with open(file_path, "w") as output_file:
            for row in output_rows:
                output_file.write(row)
        return


def build_bank(config):
    return LBBAmazonPlugin(config)
