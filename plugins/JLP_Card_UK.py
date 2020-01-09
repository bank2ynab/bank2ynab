# Plugin to work with John Lewis Partnership Card [UK]

from bank2ynab import B2YBank, EncodingCsvReader
import re
import datetime
import csv


class JLP_Card_UKPlugin(B2YBank):
    def __init__(self, config_object):
        super(JLP_Card_UKPlugin, self).__init__(config_object)
        self.name = "JLP_Card_UK"

    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        # we know it should have headers, but we respect the setting
        header_rows = self.config["header_rows"]
        output_data = []

        with EncodingCsvReader(file_path, delimiter=delim) as reader:
            for index, row in enumerate(reader):
                # skip first row if headers
                if index == 0 and header_rows != 0:
                    continue
                # skip rows with "Pending" date
                if row[0] == "Pending":
                    continue
                tmp = {}
                """
                DATE STUFF:
                YNAB's date format is "DD/MM/YYYY".
                This bank's date format is "DD-MON-YYYY".
                """
                tmp["Date"] = datetime.datetime.strptime(
                    row[0], "%d-%b-%Y"
                ).strftime("%d/%m/%Y")
                # PAYEE STUFF:
                tmp["Payee"] = row[1]
                # CATEGORY STUFF:
                tmp["Category"] = ""
                # MEMO STUFF:
                tmp["Memo"] = ""
                # AMOUNT STUFF:
                # CR means inflow (credit)
                if row[3] == "CR":
                    tmp["Outflow"] = ""
                    tmp["Inflow"] = re.sub(r"\ |\£|\+|\,", "", row[2])
                else:
                    tmp["Outflow"] = re.sub(r"\ |\£|\+|\,", "", row[2])
                    tmp["Inflow"] = ""
                # respect Output Columns option
                out_row = [""] * len(output_columns)
                for index, key in enumerate(output_columns):
                    out_row[index] = tmp.get(key, "")
                output_data.append(out_row)
            # insert the header row at the top.
            output_data.insert(0, output_columns)
        return output_data


def build_bank(config):
    return JLP_Card_UKPlugin(config)
