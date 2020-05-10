# Plugin for handling [AT Raiffeisen RCM] format

from bank2ynab import B2YBank, EncodingCsvReader


class RaiffeisenRCMPlugin(B2YBank):
    def __init__(self, config_object):
        super(RaiffeisenRCMPlugin, self).__init__(config_object)
        self.name = "RaiffeisenRCM"

    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        # we know it should have headers, but we respect the setting
        header_rows = self.config["header_rows"]
        output_data = []

        with EncodingCsvReader(file_path, delimiter=delim) as reader:
            for index, row in enumerate(reader):
                tmp = {}

                # special first row
                if index == 0 and header_rows != 0:
                    tmp["Date"] = "Date"
                    tmp["Payee"] = "Payee"
                    tmp["Category"] = "Category"
                    tmp["Memo"] = "Memo"
                    tmp["Outflow"] = "Outflow"
                    tmp["Inflow"] = "Inflow"
                    out_row = [""] * len(output_columns)
                    for index, key in enumerate(output_columns):
                        out_row[index] = tmp.get(key, "")
                    output_data.append(out_row)
                    continue

                """
                DATE STUFF:
                YNAB's date format is "DD/MM/YYYY".
                This bank's date format is "YYYMMDD" without delimiters.
                Moving the substrings into the proper order:
                https://stackoverflow.com/a/663175/20571
                """
                date = row[2]
                tmp["Date"] = date[6:8] + "-" + date[4:6] + "-" + date[0:4]
                # PAYEE STUFF:
                # fill payee if present, otherwise fill from memo:
                if row[3].strip() != "":
                    tmp["Payee"] = row[3].strip()
                else:
                    tmp["Payee"] = row[5].strip()
                # CATEGORY STUFF:
                # tmp["Category"] = '' # No category is provided.
                # MEMO STUFF:
                # concatenate two input columns into one output column:
                tmp["Memo"] = row[1].strip() + " " + row[5].strip()
                # AMOUNT STUFF:
                # tmp["Outflow"] # Outflow is provided as a negative inflow.
                # Convert from ATS to EUR:
                tmp["Inflow"] = round(float(row[4]) / 13.760300331, 2)

                # respect Output Columns option
                out_row = [""] * len(output_columns)
                for index, key in enumerate(output_columns):
                    out_row[index] = tmp.get(key, "")
                output_data.append(out_row)
        return output_data


def build_bank(config):
    return RaiffeisenRCMPlugin(config)
