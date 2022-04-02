"""
Plugin that uses information from the memo field to fill in other fields
"""

# Usage:
# Ensure the relevant bank config has a Memo Parser config attribute
# The attribute should contain a list of regular expressions, run from top to bottom
# with named groups, used to override fields in the CSV.
#   Memo Parser =
#       (?<payee>\w+) (?<memo>.*)? AT (?<time>\d{2}\.\d{2})
#       PURCHASER: (?<purchaser>\w+) AT (?<memo>.*)?
# Valid groups are: payee, memo, date, time, purchaser
# At that point, you can reference the plugin in conf files like this:
#   Plugin = parse_from_memo

import logging
import re
from datetime import datetime

from bank_handler import BankHandler, get_output_path
from dataframe_handler import read_csv
from transactionfile_reader import detect_encoding

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)


class ParseFromMemo(BankHandler):
    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(ParseFromMemo, self).__init__(config_object)

        # Parsers from the Config, skipping blank rows
        memo_parsers = list(
            filter(len, self.config_dict.get("plugin_args", []))
        )
        if len(memo_parsers) <= 0:
            raise AttributeError(
                "The plugin arguments option contained no regular expresions to use for parsing"
            )
        self.parsers_to_try = list(
            map(re.compile, memo_parsers)  # convert to regex
        )

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """
        Override the memo, date and payee columns with information read from the memo field
        """

        # Read in the old CSV
        src_encod = detect_encoding(file_path)
        df = read_csv(
            file_path=file_path,
            delim=self.config_dict.get("input_delimiter", ","),
            header_rows=0,
            footer_rows=0,
            encod=src_encod,
        )

        # Apply our adjustment
        new_df = df.apply(self._parse_from_memo, axis="columns")

        # Generate output path
        new_path = get_output_path(
            input_path=file_path,
            prefix=f"memo_parsed_csv_{self.config_dict['bank_name']}_",
            ext=".csv",
        )

        # Write the dataframe to output file
        new_df.to_csv(
            new_path,
            index=False,  # no row names (just ints)
            header=False,  # no column names (just ints)
            encoding=src_encod,
            sep=self.config_dict.get("input_delimiter", ","),
        )

        return new_path

    def _parse_from_memo(self, row):
        memo_index = self.config_dict["input_columns"].index("Memo")
        original_memo = row[memo_index]

        # Try to match all known parsers against the memo
        for parser in self.parsers_to_try:
            match = parser.search(original_memo)
            if not match:
                continue

            logging.debug(f"Matches for '{original_memo}': ")
            logging.debug(match.groups())

            # Fields that mutate the memo field
            new_memo = []
            try:
                if len(match["memo"]):
                    new_memo.append(match["memo"])
            except IndexError:
                pass

            try:
                if len(match["purchaser"]):
                    new_memo.append(f"purchased by {match['purchaser']}")
            except IndexError:
                pass

            if len(new_memo) > 0:
                row[memo_index] = " ".join(new_memo)

            # Fields that mutate the date
            try:
                if len(match["date"]):
                    date_col = self.config_dict["input_columns"].index("Date")
                    try:
                        input_date = datetime.strptime(
                            match["date"], "%d-%m-%Y"
                        )
                        new_date = datetime.strftime(
                            input_date,
                            self.config_dict.get("date_format", "%Y-%m-%d"),
                        )

                        row[date_col] = new_date
                    except ValueError as exception:
                        pass
            except IndexError:
                pass

            # Field that mutate the payee
            try:
                if len(match["payee"]):
                    payee_index = self.config_dict["input_columns"].index(
                        "Payee"
                    )

                    row[payee_index] = match["payee"]
            except IndexError:
                pass

        return row


def build_bank(config):
    return ParseFromMemo(config)
