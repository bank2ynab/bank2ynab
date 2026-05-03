# Plugin for handling OCBC Bank [SG] files

from ..bank_handler import BankHandler
from ..config_handler import BankConfig


class OCBC_Bank_SG(BankHandler):
    """Plugin for handling Oversea-Chinese Banking Corporation Singapore (OCBC SG) bank files."""

    def __init__(self, config: BankConfig):
        """Initialise OCBC Singapore bank handler.

        Args:
            config: Bank configuration parameters.
        """
        super().__init__(config)
        self.name = "OCBC_Bank_SG"

    def _preprocess_file(self, file_path, plugin_args) -> str:
        """Fix multi-line rows and strip invalid characters in the input file.

        For every row without a valid date field, strips separators and appends
        to the preceding row. Overwrites the input file with modified output.

        Args:
            file_path: Path to file.
            plugin_args: Plugin-specific arguments (unused).

        Returns:
            str: Path to the modified file.
        """
        # what do we actually want to do?
        header_rows = self.config.header_rows
        footer_rows = self.config.footer_rows

        # get total number of rows in transaction file using a generator
        with open(file_path) as row_counter:
            row_count = sum(1 for _ in row_counter)

        with open(file_path) as input_file:
            output_rows = []
            for rownum, row in enumerate(input_file):
                # strip any single quotes, e.g. if payee is MCDONALD'S
                row = row.replace("'", "")
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
        return file_path


def build_bank(config):
    """Return an OCBC_Bank_SG instance for a given bank configuration.

    Args:
        config: Dict containing all available configuration parameters.

    Returns:
        OCBC_Bank_SG: A BankHandler subclass instance.
    """
    return OCBC_Bank_SG(config)
