# with thanks to https://github.com/jpsk/Swedbank-to-YNAB4-converter/

from bank2ynab import B2YBank, CrossversionCsvReader


class SwedebankPlugin(B2YBank):
    def __init__(self, config_object, is_py2):
        super(SwedebankPlugin, self).__init__(config_object, is_py2)
        self.name = "SwedeBank"

    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        # we know it should have headers, but we respect the setting
        has_headers = self.config["has_headers"]
        output_data = []

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as reader:
            for index, row in enumerate(reader):
                # skip first row if headers
                if index == 0 and has_headers:
                    continue
                tmp = {}
                date = row[2].split('-')
                tmp["Date"] = date[2] + '/' + date[1] + '/' + date[0]
                tmp["Payee"] = row[3]
                tmp["Category"] = ''
                tmp["Memo"] = row[4]
                # if the record ID is empty, it's some sort of balance, ignore
                if row[8] == "":
                    continue

                # K is inflow, D is outflow - I guess Kredit and Debit ;)
                if row[7] == 'K':
                    tmp["Outflow"] = ''
                    tmp["Inflow"] = row[5]
                else:
                    tmp["Outflow"] = row[5]
                    tmp["Inflow"] = ''

                # respect Output Columns option
                out_row = [''] * len(output_columns)
                for index, key in enumerate(output_columns):
                    out_row[index] = tmp.get(key, "")
                output_data.append(out_row)
        return output_data


def build_bank(config, is_py2):
    return SwedebankPlugin(config, is_py2)
